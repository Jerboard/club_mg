import db
from config import conf
from init import bot
from enums import UserStatus


# банит пользователя
async def ban_user(user_id):
    try:
        await bot.ban_chat_member(conf.channel_id, user_id=user_id)
        await db.reg_action(user_id=user_id, status='successfully', action='бан')
    except Exception as ex:
        await db.reg_action (user_id=user_id, status='failed', action='бан', comment=ex)

    await db.update_user_info(
        user_id=user_id,
        status=UserStatus.NOT_SUB.value,
        recurrent=False
    )
    text = (
        f'Ваша подписка на канал {conf.channel_name} закончилась, чтобы продлить подписку нажмите /start и приобретите '
        f'новую подписку.'
    )
    try:
        photo_id = await db.get_random_photo_id()
        await bot.send_photo(chat_id=user_id, caption=text, photo=photo_id.photo_id)

    except Exception as ex:
        await db.reg_action (user_id=user_id, status='failed', action='Сообщение пользователю о бане', comment=ex)