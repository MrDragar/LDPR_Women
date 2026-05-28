import asyncio
import json
from vkbottle.bot import BotLabeler, Message
from vkbottle.dispatch import BuiltinStateDispenser
from src.application.states import PostsStates
from src.application.filters import AdminFilter
from src.services.interfaces import IUserService

router = BotLabeler()
router.auto_rules = [AdminFilter()]


@router.message(text="/post")
async def cmd_post(message: Message, state_dispenser: BuiltinStateDispenser):
    # Просим пользователя отправить сообщение, которое нужно переслать
    await state_dispenser.set(message.from_id, PostsStates.GET_MESSAGE)
    await message.answer(
        "Отправьте сообщение (текст, фото, видео и т.д.), которое нужно разослать всем пользователям:"
    )


@router.message(state=PostsStates.GET_MESSAGE)
async def confirm_post(message: Message, state_dispenser: BuiltinStateDispenser):
    # Сохраняем ВСЕ данные сообщения: текст и вложения
    # message.dict() содержит все поля, включая attachments
    msg_data = {
        "text": message.text,
        "attachments": message.attachments or [],
    }

    await state_dispenser.set(
        message.from_id,
        PostsStates.CONFIRM,
        msg_text=message.text,  # Для отображения превью
        msg_data=msg_data  # Полные данные для отправки
    )

    # Формируем красивое превью
    preview = message.text
    if message.attachments:
        preview += f"\n[Вложений: {len(message.attachments)}]"

    await message.answer(
        f"Вы уверены, что хотите разослать это сообщение?\n\n{preview}\n\nОтправьте 'Да' для подтверждения."
    )


@router.message(state=PostsStates.CONFIRM, text="Да")
async def start_mailing(message: Message, user_service: IUserService,
                        state_dispenser: BuiltinStateDispenser):
    state = await state_dispenser.get(message.from_id)

    # Извлекаем сохранённые данные
    msg_data = state.payload['msg_data']
    text = msg_data['text']
    attachments = msg_data['attachments']

    users = await user_service.get_all_users()
    total_users = len(users)

    await message.answer(f"Начинаю рассылку на {total_users} пользователей...")

    count = 0
    # Оптимизация: формируем строку attachments один раз, если она есть
    attachment_string = ""
    if attachments:
        # Преобразуем список объектов Attachment в строку формата "photo123_456,video789_012"
        attachment_string = ",".join([att.resolve_for_forward() for att in attachments])

    for u in users:
        try:
            # Отправляем сообщение с текстом и вложениями
            await message.ctx_api.messages.send(
                peer_id=u.id,
                message=text,
                attachment=attachment_string if attachment_string else None,
                random_id=0
            )
            count += 1
            # Небольшая задержка, чтобы не превысить лимиты VK API
            await asyncio.sleep(0.05)
        except Exception as e:
            # Логирование ошибки полезно для отладки
            # print(f"Ошибка при отправке пользователю {u.id}: {e}")
            pass

    await state_dispenser.delete(message.from_id)
    await message.answer(f"Рассылка завершена. Успешно отправлено: {count} из {total_users}")
