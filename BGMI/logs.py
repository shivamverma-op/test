import os
import sys
import io
import traceback
from datetime import datetime
from contextlib import redirect_stdout
from subprocess import getoutput as run
from pyrogram.enums import ChatAction
from BGMI import bot as app
from pyrogram import filters

prefix = [".", "!", "?", "*", "$", "#", "/"]

DEVS_ID = [6239769036, 7074356361, 7837238122, 6651534688]  # Add your developer IDs here


@app.on_message(filters.command("sh", prefix) & filters.user(DEVS_ID))
async def sh(_, message):
    """
    Execute shell commands and return the output.
    """
    if len(message.command) < 2:
        return await message.reply_text("No Input Found!")

    code = message.text.split(None, 1)[1]
    try:
        x = run(code)
        string = f"**📎 Input**: ```{code}```\n\n**📒 Output**:\n```{x}```"
        await message.reply_text(string)
    except Exception as e:
        error_text = f"Error executing shell command:\n{e}"
        with io.BytesIO(str.encode(error_text)) as out_file:
            out_file.name = "shell_error.txt"
            await message.reply_document(document=out_file, caption="Shell Command Error")


async def aexec(code, client, message):
    """
    Asynchronous execution of Python code.
    """
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@app.on_message(filters.command("eval", prefix) & filters.user(DEVS_ID))
async def eval(client, message):
    """
    Evaluate Python code dynamically.
    """
    if len(message.text.split()) < 2:
        return await message.reply_text("No codes found!")

    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(None, 1)[1]
    start = datetime.now()
    reply_to_ = message.reply_to_message or message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = exc or stderr or stdout or "Success"
    end = datetime.now()
    ping = (end - start).microseconds / 1000

    final_output = (
        f"📎 **Input:**\n```{cmd}```\n\n"
        f"📒 **Output:**\n```{evaluation.strip()}```\n\n"
        f"✨ **Taken Time:** {ping}ms"
    )
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval_output.txt"
            await reply_to_.reply_document(document=out_file, caption="Eval Output")
    else:
        await status_message.edit_text(final_output)


@app.on_message(filters.command(["log", "logs"], prefix) & filters.user(DEVS_ID))
async def logs(app, message):
    """
    Fetch the latest logs from the log file.
    """
    try:
        run_logs = run("tail -n 20 logs.txt")  # Fetch the last 20 lines of logs
        await message.reply_text(f"📒 **Latest Logs:**\n```{run_logs}```")
    except Exception as e:
        await message.reply_text(f"Error fetching logs:\n`{e}`")


@app.on_message(filters.command(["flogs", "flog"], prefix) & filters.user(DEVS_ID))
async def flogs(app, message):
    """
    Fetch and send the full log file as a document.
    """
    try:
        run_logs = run("cat logs.txt")  # Fetch the entire log file
        text = await message.reply_text("Sending Full Logs...")
        await app.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
        with io.BytesIO(str.encode(run_logs)) as logs:
            logs.name = "full_logs.txt"
            await message.reply_document(document=logs, caption="Full Logs")
        await text.delete()
    except Exception as e:
        await message.reply_text(f"Error fetching full logs:\n`{e}`")
