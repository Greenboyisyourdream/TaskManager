import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers import (
        send_notification,
        register_current_page_error,
        register_del_message,
        register_del_task,
        register_faq,
        register_main_menu,
        register_show_current_task,
        register_show_first_task,
        register_task_date,
        register_task_description,
        register_task_enter,
        register_task_name,
        register_task_region,
        )
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.scheduler import SchedulerMiddleware

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, scheduler):
    dp.setup_middleware(DbMiddleware())
    dp.setup_middleware(SchedulerMiddleware(scheduler))
    

def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_faq(dp)
    register_main_menu(dp)
    register_del_task(dp)
    register_del_message(dp),
    register_current_page_error(dp)
    register_show_current_task(dp)
    register_show_first_task(dp)
    register_task_enter(dp)
    register_task_name(dp)
    register_task_description(dp)
    register_task_region(dp)
    register_task_date(dp)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_notification, "interval", seconds=10, args=(bot,))

    bot['config'] = config

    register_all_middlewares(dp, scheduler)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
