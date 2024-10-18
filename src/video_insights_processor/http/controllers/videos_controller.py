import logging
from logging import Logger
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException

from .app_base_controller import AppBaseController
from ..adapters.video_adapter import VideoAdapter
from ..dtos.video_dto import VideoDto
from ..dtos.video_insights_state_dto import VideoInsightsStateDto
from ...video_service.domain.video import Video
from ...video_service.domain.video_insights_state import VideoInsightsState
from ...video_service.exceptions.video_already_exists_exception import VideoAlreadyExistsException
from ...video_service.exceptions.video_not_found_exception import VideoNotFoundException
from ...video_service.use_cases.video_insights_extractor import VideoInsightsExtractor
from ...video_service.use_cases.video_insights_state_getter import VideosInsightsStateGetter
from ...video_service.use_cases.videos_adder import VideosAdder
from ...video_service.use_cases.videos_deleter import VideosDeleter
from ...video_service.use_cases.videos_getter import VideosGetter


class VideosController(AppBaseController):
    _log: Logger = logging.getLogger(__name__)
    _api_router: APIRouter = APIRouter(prefix='/api/videos', tags=['videos'])
    _video_adapter: VideoAdapter

    def __init__(self, video_adapter: VideoAdapter = VideoAdapter()) -> None:
        self._api_router.add_api_route(path='', endpoint=self.get_all_videos, methods=['GET'])
        self._api_router.add_api_route(path='', endpoint=self.add_video, methods=['PUT'])
        self._api_router.add_api_route(path='/{video_id}', endpoint=self.delete_video, methods=['DELETE'])
        self._api_router.add_api_route(
            path='/{video_id}/insights',
            endpoint=self.extract_video_insights,
            methods=['PUT']
        )
        self._api_router.add_api_route(
            path='/{video_id}/insights/state',
            endpoint=self.get_video_insights_state,
            methods=['GET']
        )
        self._video_adapter = video_adapter

    @property
    def api_router(self) -> APIRouter:
        return self._api_router

    async def get_all_videos(self) -> list[VideoDto]:
        self._log.info('Getting all videos...')
        try:
            result: list[VideoDto] = [self._video_adapter.adapt_video(x) for x in await VideosGetter().get_all_videos()]
            self._log.info('All videos retrieved')
            return result
        except Exception as exception:
            self._log.error(f'Exception found while getting all videos: {self._format_exception(exception)}')
            raise HTTPException(status_code=500, detail=self._format_exception(exception))

    async def add_video(self, video_dto: VideoDto) -> None:
        self._log.info(f'Adding {video_dto}...')
        try:
            await VideosAdder().add_video(self._video_adapter.adapt_video_dto(video_dto))
            self._log.info(f'{video_dto} added')
        except VideoAlreadyExistsException as exception:
            self._log.error(f'Exception found while adding {video_dto}: {self._format_exception(exception)}')
            raise HTTPException(status_code=409, detail=self._format_exception(exception))
        except Exception as exception:
            self._log.error(f'Exception found while adding {video_dto}: {self._format_exception(exception)}')
            raise HTTPException(status_code=500, detail=self._format_exception(exception))

    async def delete_video(self, video_id: UUID) -> None:
        self._log.info(f'Deleting video \'{video_id}\'...')
        try:
            await VideosDeleter().delete_video(video_id)
            self._log.info(f'Video \'{video_id}\' deleted')
        except VideoNotFoundException as exception:
            self._log.error(f'Exception found while deleting video \'{video_id}\': {self._format_exception(exception)}')
            raise HTTPException(status_code=404, detail=self._format_exception(exception))
        except Exception as exception:
            self._log.error(f'Exception found while deleting video \'{video_id}\': {self._format_exception(exception)}')
            raise HTTPException(status_code=500, detail=self._format_exception(exception))

    async def extract_video_insights(self, video_id: UUID, background_tasks: BackgroundTasks) -> None:
        self._log.info(f'Scheduling background task to extract insights from video \'{video_id}\'...')
        try:
            video: Video | None = next((x for x in await VideosGetter().get_all_videos() if x.id == video_id), None)
            if video is None:
                raise VideoNotFoundException(video_id)
            video_insights_extractor: VideoInsightsExtractor = VideoInsightsExtractor()
            background_tasks.add_task(func=video_insights_extractor.extract_video_insights, video=video)
            self._log.info(f'Background task to extract insights from video \'{video_id}\' scheduled')
        except VideoNotFoundException as exception:
            self._log.error(
                f'Exception found while scheduling background task to extract insights from video \'{video_id}\': '
                f'{self._format_exception(exception)}'
            )
            raise HTTPException(status_code=404, detail=self._format_exception(exception))
        except Exception as exception:
            self._log.error(
                f'Exception found while scheduling background task to extract insights from video \'{video_id}\': '
                f'{self._format_exception(exception)}'
            )
            raise HTTPException(status_code=500, detail=self._format_exception(exception))

    async def get_video_insights_state(self, video_id: UUID) -> VideoInsightsStateDto:
        self._log.info(f'Getting insights state for video \'{video_id}\'...')
        try:
            video_insights_state: VideoInsightsState = await VideosInsightsStateGetter().get_video_insights_state(
                video_id
            )
            result: VideoInsightsStateDto = VideoInsightsStateDto(
                video_id=video_id,
                video_insights_state=video_insights_state.value
            )
            self._log.info(f'Insights state for video \'{video_id}\' retrieved')
            return result
        except VideoNotFoundException as exception:
            self._log.error(
                f'Exception found while getting insights state for video \'{video_id}\': '
                f'{self._format_exception(exception)}'
            )
            raise HTTPException(status_code=404, detail=self._format_exception(exception))
        except Exception as exception:
            self._log.error(
                f'Exception found while getting insights state for video \'{video_id}\': '
                f'{self._format_exception(exception)}'
            )
            raise HTTPException(status_code=500, detail=self._format_exception(exception))
