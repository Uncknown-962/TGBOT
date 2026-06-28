from aiogram import Router

from . import start, stats, settings, admin, support, faq, notes, dice, profile, common


def setup_routers() -> Router:
    router = Router()

    router.include_router(start.router)
    router.include_router(stats.router)
    router.include_router(settings.router)
    router.include_router(admin.router)
    router.include_router(support.router)
    router.include_router(faq.router)
    router.include_router(notes.router)
    router.include_router(dice.router)
    router.include_router(profile.router)
    router.include_router(common.router)

    return router
