import logging
import re
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import FloodWait, BadRequest
from pyrogram.types import ChatPermissions, Message

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

api_id = ""
api_hash = ""
bot_token = ""
specified_ids = []

app = Client("Botest", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


@app.on_message(filters.group & filters.new_chat_members)
async def auto_leave_non_whitelisted_groups(_, message):
    for member in message.new_chat_members:
        if member.id == (await app.get_me()).id:  # 如果新的 group member 是自己
            if str(message.chat.id) not in specified_ids:  # 如果该 group 不在白名单
                await app.leave_chat(message.chat.id)  # 则离开该 group


def parse_time(time_str):
    time_multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    unit = time_str[-1]
    if unit in time_multiplier and time_str[:-1].isdigit():
        return int(time_str[:-1]) * time_multiplier[unit]
    else:
        return None


def get_sender_id(message):
    sender_id = None
    if message.from_user:
        sender_id = message.from_user.id
    elif message.sender_chat:
        sender_id = message.sender_chat.id
    return sender_id


async def check_admin(client: Client, message: Message):
    if message.sender_chat:
        # 检查 sender_chat.id 是否在指定的ID列表中
        if message.sender_chat.id in specified_ids:
            return True
        else:
            return False
    elif message.from_user:
        try:
            chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
            is_admin = chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
            return is_admin
        except Exception as e:
            return False
    else:
        return False


def generate_custom_response(message):
    if message.from_user is None:
        if message.sender_chat is None:
            return "这人不熟"
        else:
            chat_type = message.sender_chat.type
            if chat_type == ChatType.CHANNEL:
                return message.sender_chat.title
            elif chat_type in [ChatType.SUPERGROUP, ChatType.GROUP]:
                signature = message.author_signature if hasattr(message, 'author_signature') else '一个无名人士'
                return signature
            else:
                return "不知道什么人"
    else:
        last_name = message.from_user.last_name if message.from_user.last_name else ""
        full_name = f"[{message.from_user.first_name} {last_name}](tg://user?id={message.from_user.id})"
        return full_name


async def auto_delete_message(message, response):
    await asyncio.sleep(10)  # Wait for 10 seconds
    await message.delete()  # Delete the message
    await response.delete()  # Delete the message


async def handle_abuse_command(client: Client, message: Message):
    await message.delete()  # Delete the message
    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=get_sender_id(message.reply_to_message),
            permissions=ChatPermissions(),
            until_date=datetime.now() + timedelta(seconds=60)
        )
        muted_user_response = generate_custom_response(message.reply_to_message)
        response_message = f"{muted_user_response} 因为 假装蓝拳 被塞入 60秒 口球。"
        response = await message.reply_text(response_message)
        await asyncio.sleep(10)  # Wait for 10 seconds
        await response.delete()  # Delete the message
    except Exception as e:
        await message.reply_text("执行禁言操作失败。")


@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client: Client, message: Message):
    if not await check_admin(client, message):
        await message.reply_text("只有管理员可以使用此命令。")
        return
    if not message.reply_to_message:
        await message.reply_text("没有发现可以塞入口球的嘴！")
        return
    if await check_admin(client, message.reply_to_message):
        await message.reply_text("你要不要看看你在做什么！")
        return

    mute_reason = "权力的一次小小任性"  # 默认理由
    mute_duration = 0  # 默认永久
    command_parts = message.text.split(maxsplit=3)

    if len(command_parts) >= 2:
        parsed_time = parse_time(command_parts[1])
        if parsed_time is not None:
            mute_duration = parsed_time
            if len(command_parts) == 3:
                mute_reason = command_parts[2]  # 用户指定了理由
        else:
            if len(command_parts) == 2:
                mute_reason = command_parts[1]  # 用户仅指定了理由

    # use datetime api
    until_date = datetime.now() + timedelta(seconds=mute_duration if mute_duration > 30 else 30)

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=get_sender_id(message.reply_to_message),
            permissions=ChatPermissions(),
            until_date=until_date
        )
        muted_user_response = generate_custom_response(message.reply_to_message)
        admin_response = generate_custom_response(message)
        duration_display = f"{mute_duration}秒" if mute_duration > 0 else "永久"
        response_message = f"{muted_user_response} 因为 {mute_reason} 被 {admin_response} 塞入了 {duration_display} 的口球。"
        response = await message.reply_text(response_message)
        await auto_delete_message(message, response)
    except Exception as e:
        await message.reply_text("执行禁言操作失败。")


@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client: Client, message: Message):
    if not await check_admin(client, message):
        # await message.reply_text("不许乱玩指令，小心被禁言！")
        await handle_abuse_command(client, message)
        return
    if not message.reply_to_message:
        await message.reply_text("尚未锁定目标，请您指示！")
        return
    if await check_admin(client, message.reply_to_message):
        await message.reply_text("你要不要看看你在做什么！")
        return

    target_user_id = get_sender_id(message.reply_to_message)
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "权力的又一次小小任性"

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target_user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_send_polls=True,
                can_add_web_page_previews=True,
                can_invite_users=True,
            )
        )

        unmute_user_response = generate_custom_response(message.reply_to_message)
        admin_response = generate_custom_response(message)
        response_message = f"{unmute_user_response} 因为 {reason} 被 {admin_response} 拔出了口球。"
        response = await message.reply_text(response_message)
        await auto_delete_message(message, response)
    except Exception as e:
        await message.reply_text("执行解除禁言操作失败。")


@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client: Client, message: Message):
    if not await check_admin(client, message):
        # await message.reply_text("不许乱玩指令，小心被禁言！")
        await handle_abuse_command(client, message)
        return
    if not message.reply_to_message:
        await message.reply_text("尚未锁定目标，请您指示！")
        return
    if await check_admin(client, message.reply_to_message):
        await message.reply_text("你要不要看看你在做什么！")
        return

    target_user_id = get_sender_id(message.reply_to_message)

    try:
        chat_id = message.chat.id
        await client.ban_chat_member(chat_id, target_user_id)

        # 调用 generate_custom_response 函数生成对被封禁用户的描述
        custom_response = generate_custom_response(message.reply_to_message)
        # 将生成的描述发送给执行封禁命令的用户
        await message.reply_text(f"{custom_response} 已被封禁。")
    except FloodWait as e:
        await message.reply_text("请稍后再试。")
    except BadRequest as e:
        await message.reply_text("封禁操作失败。")


@app.on_message(filters.regex(r'^([+-])\s*(\d*)\s*(.*)$') & filters.group)
async def handle_change_balance(client: Client, message: Message):
    """
    +/- 数字 文字
    被回复消息的人 增加/失去了 文字
    没有数字则使用 一些
    没有文字则使用 积分
    """
    # 使用正则表达式匹配消息
    match = re.match(r'^([+-])\s*(\d*)\s*(.*)$', message.text)
    if match:
        sign, amount, currency = match.groups()
        action = "获得了" if sign == '+' else "失去了"
        amount = (" " + amount + " ") if amount else "一些"  # 如果没有指定数量，则默认为"一些"
        currency = currency if currency else "积分"  # 如果没有指定货币/文本，则默认为"积分"
    else:
        await message.reply_text("请规范玩弄姿势。")
        return

    # 确定目标用户：如果是回复消息，则目标是被回复的用户；否则，目标是发送指令的用户
    user_response = generate_custom_response(message.reply_to_message if message.reply_to_message else message)

    try:
        response_message = f"{user_response} {action}{amount}{currency}。"
        await message.reply_text(response_message)
    except Exception as e:
        await message.reply_text("玩弄失败！")


@app.on_message(filters.regex(r'^dubo$') & filters.group)
async def dubo(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("尚未指定目标！")
        await asyncio.sleep(3)
        await message.delete()
        return

    try:
        user_a = generate_custom_response(message.reply_to_message)
        user_b = generate_custom_response(message)
        await message.reply_text(f"请 {user_a} 和 {user_b} 使用 🎲回复此条消息。")
    except FloodWait as e:
        await message.reply_text("请稍后再试。")
    except BadRequest as e:
        await message.reply_text("操作失败。")


@app.on_message(filters.dice & filters.group)
async def battle(client: Client, message: Message):
    if not message.reply_to_message:
        return

    my_bot = await app.get_me()
    if message.reply_to_message.from_user.id != my_bot.id:
        return

    user_b = message.reply_to_message.reply_to_message.from_user
    # print("message.reply_to_message.reply_to_message: ", message.reply_to_message.reply_to_message)
    user_a = message.reply_to_message.reply_to_message.reply_to_message.from_user
    # print("message.reply_to_message.reply_to_message.reply_to_message: ", message.reply_to_message.reply_to_message.reply_to_message)
    if message.from_user.id not in [user_a.id, user_b.id]:
        return

    try:
        reply_chat_id = message.reply_to_message.chat.id
        message_id = message.reply_to_message.id
        last_name = message.from_user.last_name if message.from_user.last_name else ""
        user = f"{message.from_user.first_name} {last_name}"
        user_dice = message.dice.value

        message_text = message.reply_to_message.text
        match = re.match(r'^(.+)的分数为 (\d+)$', message_text)
        if match:
            other_user = match.group(1)
            other_user_dice = int(match.group(2))
            if other_user_dice > user_dice:
                text = f"{other_user} 赢。{other_user}的分数为 {other_user_dice}，{user}的分数为 {user_dice}。"
            elif other_user_dice < user_dice:
                text = f"{user} 赢。{other_user}的分数为 {other_user_dice}，{user}的分数为 {user_dice}。"
            else:
                text = f"平局。{other_user}的分数为 {other_user_dice}，{user}的分数为 {user_dice}。"
            await message.reply_text(text)
        else:
            text = f"{user}的分数为 {user_dice}"
            await app.edit_message_text(reply_chat_id, message_id, text)
    except FloodWait as e:
        await message.reply_text("请稍后再试。")
    except BadRequest as e:
        await message.reply_text("操作失败。")


app.run()
