"""Wheel Lottery module - Color wheel lottery system."""

from routes.wheel_lottery.wheel_lottery_routes import (init_wheel_config,
                                                       wheel_lottery_bp)

__all__ = ["wheel_lottery_bp", "init_wheel_config"]
