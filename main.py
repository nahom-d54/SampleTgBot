from contextlib import asynccontextmanager
from http import HTTPStatus
from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram.ext._contexttypes import ContextTypes
from fastapi import FastAPI, Request, Response
import os
import uvicorn

token = os.environ.get("BOT_TOKEN")
ptb = None

@asynccontextmanager
async def lifespan(_):
    await ptb.bot.setWebhook(url=os.environ.get("WEBHOOK_URL"))
    #secret_token=os.environ.get("SECRET_TOKEN")) # replace <your-webhook-url>
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()

app = FastAPI(lifespan=lifespan)
@app.on_event("startup")
async def startup_event():
    global ptb
    ptb = (
        Application.builder()
        .updater(None)
        .token(token)
        .read_timeout(7)
        .get_updates_read_timeout(43)
        .build()
    )
    ptb.add_handler(CommandHandler("start", start))
@app.post("/")
async def process_update(request: Request):
    # protection
    #headers = request.headers
    #secret_token = headers.get("X-Telegram-Bot-Api-Secret-Token")
    #if secret_token != os.environ.get("SECRET_TOKEN"):
        #return Response(status_code=HTTPStatus.UNAUTHORIZED)
    #protection end
    
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)

async def start(update, _: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(f"Hello { update.message.chat.first_name }")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
