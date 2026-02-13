import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 設定管理員 ID
ADMIN_ID = 8976450
# 儲存使用者 chat_id 的集合 (建議改用資料庫儲存)
user_list = set()

# 廣播指令邏輯
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # 1. 權限驗證
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ 您沒有權限使用此指令。")
        return

    # 2. 獲取廣播內容
    # 指令用法為: /broadcast 大家好，這是一則公告
    broadcast_msg = ' '.join(context.args)
    if not broadcast_msg:
        await update.message.reply_text("❓ 請在指令後輸入要廣播的文字。範例: /broadcast 訊息內容")
        return

    # 3. 執行廣播
    count = 0
    for chat_id in user_list:
        try:
            # 排除發送給自己，避免重複
            if chat_id != ADMIN_ID:
                await context.bot.send_message(
                    chat_id=chat_id, 
                    text=f"📢 【系統廣播】\n\n{broadcast_msg}\n\n(您可以直接回覆此訊息與管理員對話)"
                )
                count += 1
        except Exception as e:
            print(f"發送給 {chat_id} 失敗: {e}")

    await update.message.reply_text(f"✅ 廣播完成，已發送給 {count} 位使用者。")

# 處理回覆訊息
async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    text = update.message.text

    # 將每位使用過機器人的 chat_id 存起來
    user_list.add(update.effective_chat.id)

    # 如果是非管理員回覆訊息，則轉發給管理員
    if user_id != ADMIN_ID:
        forward_text = f"📩 【收到回覆】\n來自: {user_name} ({user_id})\n內容: {text}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=forward_text)
    else:
        # 如果管理員直接打字 (非指令)，可以視為一般處理
        pass

if __name__ == '__main__':
    # 替換成您的 Bot Token
    application = ApplicationBuilder().token('YOUR_BOT_TOKEN').build()
    
    # 註冊廣播指令
    application.add_handler(CommandHandler("broadcast", broadcast))
    
    # 註冊回覆訊息處理 (所有文字訊息)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_reply))
    
    application.run_polling()
