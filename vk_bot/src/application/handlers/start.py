import asyncio
import logging
from vkbottle.bot import BotLabeler, Message
from vkbottle import PhotoMessageUploader
from vkbottle.dispatch import BuiltinStateDispenser

from src.application.keyboards.personal_data_keyboard import get_personal_data_keyboard
from src.application.keyboards.miniapp_keyboard import get_miniapp_keyboard
from src.application.states import RegistrationStates
from src.services.interfaces import IUserService

router = BotLabeler()
start_command_router = BotLabeler()
logger = logging.getLogger(__name__)


@router.message()
@start_command_router.message(text=["Начать", "/start", "start", "начать", "Заново", "заново"])
async def start(
        message: Message, user_service: IUserService, 
        state_dispenser: BuiltinStateDispenser, photo_uploader: PhotoMessageUploader
):
    if message.peer_id < 0:
        return

    if await user_service.is_user_exists(message.from_id):
        await message.answer(
            "Вы уже зарегистрированы"
        )
        return
    await message.answer(
        """Сегодня мы предлагаем не просто поддержать инициативу.

Мы приглашаем Вас стать ее лицом.

Если вы считаете, что российские женщины заслуживают уважения, достойной работы, защищенного материнства и уверенности в завтрашнем дне — присоединяйтесь к инициативе ЛДПР.

Станьте волонтером поддержки семьи, расскажите о ней в своих коллективах, приводите 
единомышленников и делитесь своими историями.

Вместе мы можем сделать так, чтобы голос женщин был услышан."""
    )
    await asyncio.sleep(0.5)
    await message.answer("После регистрации вы получите статус волонтера и методические "
                         "рекомендации по продвижению нашей инициативы.")
    await message.answer("Если вы допустили ошибку при заполнении анкеты, напишите мне 'Заново' или 'Начать'")
    await message.answer(
        "Для начала дайте согласие на обработку персональных данных",
        keyboard=get_personal_data_keyboard()
    )
    await state_dispenser.set(message.from_id, RegistrationStates.PERSONAL_DATA)
