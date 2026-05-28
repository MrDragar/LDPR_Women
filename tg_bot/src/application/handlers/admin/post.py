import asyncio
import json
import logging
from datetime import timedelta, timezone, datetime

from aiogram import Router, types, F, filters
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from src.application.keyboards.admin.post_keyboard import get_post_keyboard
from src.application.states import PostsStates
from src.services.interfaces import IUserService

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(filters.Command('cancel'))
@router.message(PostsStates.confirm, F.text.lower().strip() == 'отменить')
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Отмена рассылки", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(filters.Command('post'))
async def start_post_dialog_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите сообщение для рассылки")
    await state.set_state(PostsStates.get_message)


@router.message(PostsStates.get_message)
async def get_message_handler(message: types.Message, state: FSMContext):
    await message.answer("Подтвердите началу рассылки. Ваше сообщение:", reply_markup=get_post_keyboard())
    await message.bot.copy_message(message.chat.id, message.chat.id, message.message_id)
    await state.update_data(message_id=message.message_id)
    await state.set_state(PostsStates.confirm)


@router.message(PostsStates.confirm, F.text.lower().strip() == 'подтвердить')
async def confirm_post_handler(
        message: types.Message, state: FSMContext, user_service: IUserService
):
    users = await user_service.get_all_users()
    message_id = (await state.get_data())['message_id']
    await state.clear()
    await message.answer(f"Начинаю рассылку на {len(users)} пользователей", reply_markup=ReplyKeyboardRemove())
    success_count = 0
    good_id = []
    bad_id = []
    count = 0
    for user in users:
        await asyncio.sleep(0.2)
        logger.info(f"Checking {user.id}")
        try:
            sent_message = await message.bot.copy_message(user.id, message.chat.id, message_id, disable_notification=True)
            good_id.append(user.id)
            success_count += 1
        except Exception as e:
            logger.debug(e)
            bad_id.append(user.id)
        count += 1
        if count % 100 == 0:
            await message.answer(f"Обработано {count}")

    await message.answer(f"Рассылка завершена. Отправлено "
                         f"успешно {success_count} сообщений из "
                         f"{len(users)}")

    results = {
        "total_users": len(users),
        "success_count": success_count,
        "failed_count": len(users) - success_count,
        "successful_ids": good_id,
        "failed_users": bad_id,
        "timestamp": datetime.now().isoformat()
    }

    results_json = json.dumps(results, ensure_ascii=False, indent=2)
    json_file = types.BufferedInputFile(
        results_json.encode('utf-8'),
        filename=f"mailing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    await message.answer_document(json_file, caption="📋 Результаты рассылки")


@router.message(PostsStates.confirm)
async def wait_confirm_post_handler(
        message: types.Message
):
    await message.answer("Подтвердите началу рассылки.", reply_markup=get_post_keyboard())