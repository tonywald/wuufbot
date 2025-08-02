import logging
from telegram import Update, User
from telegram.constants import ChatType, ChatMemberStatus, ParseMode
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes

from ..core.utils import _can_user_perform_action, resolve_user_with_telethon, create_user_html_link, send_safe_reply, safe_escape
from ..core.decorators import check_module_enabled, command_control
from ..core.handlers import custom_handler

logger = logging.getLogger(__name__)


# --- KICK COMMAND FUNCTIONS ---
@check_module_enabled("kicks")
@custom_handler("kick")
async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user_who_kicks = update.effective_user
    message = update.message
    if not message: return

    if chat.type == ChatType.PRIVATE:
        await send_safe_reply(update, context, text="Huh? You can't kick in private chat...")
        return

    if not await _can_user_perform_action(update, context, 'can_restrict_members', "Why should I listen to a person with no privileges for this? You need 'can_restrict_members' permission."):
        return

    target_user: User | None = None
    args_after_target: list[str] = []

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        if context.args:
            args_after_target = context.args
    elif context.args:
        target_input = context.args[0]
        if len(context.args) > 1:
            args_after_target = context.args[1:]
        
        target_user = await resolve_user_with_telethon(context, target_input, update)
        
        if not target_user and target_input.isdigit():
            try:
                target_user = await context.bot.get_chat(int(target_input))
            except:
                logger.warning(f"Could not resolve full profile for ID {target_input} in KICK. Proceeding with ID only.")
                target_user = User(id=int(target_input), first_name="", is_bot=False)
    else:
        await send_safe_reply(update, context, text="Usage: /kick <ID/@username/reply> [reason]")
        return

    if not target_user:
        await send_safe_reply(update, context, text=f"Skrrrt... I can't find the user.")
        return

    reason: str = " ".join(args_after_target) or "No reason provided."

    if not isinstance(target_user, User):
        await send_safe_reply(update, context, text="🧐 Kick can only be applied to users.")
        return

    if target_user.id == context.bot.id or target_user.id == user_who_kicks.id:
        await send_safe_reply(update, context, text="Nuh uh... This user cannot be kicked."); return

    try:
        target_chat_member = await context.bot.get_chat_member(chat.id, target_user.id)
        if target_chat_member.status in ["creator", "administrator"]:
            await send_safe_reply(update, context, text="WHAT? Chat Creator and Administrators cannot be kicked.")
            return
    except TelegramError as e:
        if "user not found" in str(e).lower():
            user_display = create_user_html_link(target_user)
            await send_safe_reply(update, context, text=f"User {user_display} is not in this chat, cannot be kicked.", parse_mode=ParseMode.HTML)
            return
        logger.warning(f"Could not get target's chat member status for /kick: {e}")

    try:
        await context.bot.ban_chat_member(chat_id=chat.id, user_id=target_user.id)
        await context.bot.unban_chat_member(chat_id=chat.id, user_id=target_user.id, only_if_banned=True)

        user_display_name = create_user_html_link(target_user)
        response_lines = ["Success: User Kicked", f"<b>• User:</b> {user_display_name} [<code>{target_user.id}</code>]", f"<b>• Reason:</b> {safe_escape(reason)}"]
        await send_safe_reply(update, context, text="\n".join(response_lines), parse_mode=ParseMode.HTML)
    except TelegramError as e:
        await send_safe_reply(update, context, text=f"Failed to kick user: {safe_escape(str(e))}")

@check_module_enabled("kicks")
@command_control("kickme")
@custom_handler("kickme")
async def kickme_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user_to_kick = update.effective_user

    if not user_to_kick:
        return

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text("Huh? You can't kick yourself in private chat...")
        return

    try:
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if not (bot_member.status == "administrator" and getattr(bot_member, 'can_restrict_members', False)):
            await update.message.reply_text("Error: I can't kick users here because I'm not an admin with ban/kick permissions 🤓.")
            return
    except TelegramError as e:
        logger.error(f"Error checking bot's own permissions in /kickme for chat {chat.id}: {e}")
        await update.message.reply_text("Error: Couldn't verify my own permissions 🤕.")
        return

    try:
        user_chat_member = await context.bot.get_chat_member(chat.id, user_to_kick.id)
        
        if user_chat_member.status == "creator":
            await update.message.reply_text("Hold Up! As the chat Creator, you must use Telegram's native 'Leave group' option.")
            return
        if user_chat_member.status == "administrator":
            await update.message.reply_text("Hold Up! As a chat Administrator, you can't use /kickme. Please use Telegram's 'Leave group' option to prevent accidental self-removal.")
            return
            
    except TelegramError as e:
        if "user not found" in str(e).lower():
            logger.warning(f"User {user_to_kick.id} not found in chat {chat.id} for /kickme, though they sent the command.")
            await update.message.reply_text("🧐 It seems you're not in this chat anymore.")
            return
        else:
            logger.error(f"Error checking your status in this chat for /kickme: {e}")
            await update.message.reply_text("Skrrrt... Couldn't verify your status in this chat to perform /kickme.")
            return

    try:
        user_display_name = create_user_html_link(user_to_kick)
        
        await update.message.reply_text(f"Done! {user_display_name}, as you wish... You have been kicked from the chat.", parse_mode=ParseMode.HTML)
        
        await context.bot.ban_chat_member(chat_id=chat.id, user_id=user_to_kick.id)
        await context.bot.unban_chat_member(chat_id=chat.id, user_id=user_to_kick.id, only_if_banned=True)
        
        logger.info(f"User {user_to_kick.id} self-kicked from chat {chat.id} ('{chat.title}')")
        
    except TelegramError as e:
        logger.error(f"Failed to self-kick user {user_to_kick.id} from chat {chat.id}: {e}")
        await update.message.reply_text(f"Error: I tried to help you leave, but something went wrong: {safe_escape(str(e))}")
    except Exception as e:
        logger.error(f"Unexpected error in /kickme for user {user_to_kick.id}: {e}", exc_info=True)
        await update.message.reply_text("Error: An unexpected error occurred while trying to process your /kickme request.")


# --- HANDLER LOADER ---
def load_handlers(application: Application):
    application.add_handler(CommandHandler("kick", kick_command))
    application.add_handler(CommandHandler("kickme", kickme_command))
