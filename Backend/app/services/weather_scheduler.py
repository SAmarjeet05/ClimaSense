"""
Background Task Scheduler for Real-Time Weather Updates
Uses APScheduler to automatically refresh weather data every 30 minutes
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class WeatherUpdateScheduler:
    """Manages scheduled weather updates"""
    
    instance = None
    scheduler = None
    
    def __new__(cls):
        """Singleton pattern - only one scheduler instance"""
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.scheduler = BackgroundScheduler()
        return cls.instance
    
    @staticmethod
    def start_scheduler(db_session_maker):
        """
        Start the background scheduler for weather updates
        
        Args:
            db_session_maker: SQLAlchemy session maker
        """
        try:
            scheduler_instance = WeatherUpdateScheduler()
            
            if scheduler_instance.scheduler.running:
                logger.info("⏱️ Scheduler already running")
                return
            
            # Import here to avoid circular imports
            from app.services.realtime_weather_service import RealtimeWeatherService
            
            def update_weather_job():
                """Job function that runs the weather update"""
                try:
                    logger.info(f"🌍 Starting scheduled weather update at {datetime.now()}")
                    
                    db = db_session_maker()
                    try:
                        results = RealtimeWeatherService.update_all_cities_from_api(db)
                        logger.info(f"✅ Weather update successful: {results['created']} created, {results['updated']} updated, {results['failed']} failed")
                    finally:
                        db.close()
                        
                except Exception as e:
                    logger.error(f"❌ Scheduled weather update failed: {str(e)}")
            
            # Add job to run every 30 minutes
            scheduler_instance.scheduler.add_job(
                update_weather_job,
                trigger=IntervalTrigger(minutes=30),
                id="weather_update_job",
                name="Update real-time weather data",
                replace_existing=True,
                max_instances=1
            )
            
            # Start the scheduler
            scheduler_instance.scheduler.start()
            logger.info("✅ Weather update scheduler started - Updates every 30 minutes")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {str(e)}")
    
    @staticmethod
    def stop_scheduler():
        """Stop the background scheduler"""
        try:
            scheduler_instance = WeatherUpdateScheduler()
            if scheduler_instance.scheduler and scheduler_instance.scheduler.running:
                scheduler_instance.scheduler.shutdown()
                logger.info("⏹️ Weather scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
    
    @staticmethod
    def get_next_run_time():
        """Get the next scheduled run time"""
        try:
            scheduler_instance = WeatherUpdateScheduler()
            if scheduler_instance.scheduler.running:
                jobs = scheduler_instance.scheduler.get_jobs()
                if jobs:
                    return jobs[0].next_run_time
            return None
        except Exception as e:
            logger.error(f"Error getting next run time: {str(e)}")
            return None
    
    @staticmethod
    def is_running():
        """Check if scheduler is running"""
        try:
            scheduler_instance = WeatherUpdateScheduler()
            return scheduler_instance.scheduler.running if scheduler_instance.scheduler else False
        except Exception as e:
            logger.error(f"Error checking scheduler status: {str(e)}")
            return False
