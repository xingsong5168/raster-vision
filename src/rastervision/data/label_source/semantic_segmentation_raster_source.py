from typing import (List, Union)

import numpy as np

from rastervision.core.box import Box
from rastervision.core.class_map import ClassMap
from rastervision.data.label_source import SegmentationClassTransformer
from rastervision.data.label_source import LabelSource
from rastervision.data.raster_source import RasterSource


class SemanticSegmentationRasterSource(LabelSource):
    """A read-only label source for segmentation raster files.
    """

    def __init__(self,
                 source: RasterSource,
                 source_class_map: ClassMap,
                 rgb: bool = False):
        """Constructor.

        Args:
            source: (RasterSource) assumed to have RGB values that are mapped to
                class_ids using the source_class_map
            source_class_map: (ClassMap) of class_ids to names.
                              Must have color values filled in
                              for usage  with rgb=True
        """
        self.source = source
        self.class_transformer = SegmentationClassTransformer(source_class_map)
        self.rgb = rgb

    def enough_target_pixels(self, window: Box, target_count_threshold: int,
                             target_classes: List[int]) -> bool:
        """Given a window, answer whether the window contains enough pixels in
        the target classes.

        Args:
             window: The larger window from-which the sub-window will
                  be clipped.
             target_count_threshold:  Minimum number of target pixels.
             target_classes: The classes of interest.  The given
                  window is examined to make sure that it contains a
                  sufficient number of target pixels.
        Returns:
             True (the window does contain interesting pixels) or False.
        """
        img = self.source.get_raw_chip(window)
        if self.rgb:
            labels = self.class_transformer.rgb_to_class(img)
        else:
            labels = img[:, :, 0].reshape(img.shape[0], img.shape[1])

        target_count = 0
        for class_id in target_classes:
            target_count = target_count + (labels == class_id).sum()

        return target_count >= target_count_threshold

    def get_labels(self, window: Union[Box, None] = None) -> np.ndarray:
        """Get labels from a window.

        If window is not None then a label window is clipped from
        the source. If window is None then assume window is full extent.

        Args:
             window: Either None or a window given as a Box object.
        Returns:
             np.ndarray of shape [height, width] where values are class ids
        """
        if window is None:
            img = self.source.get_raw_image_array()
        else:
            img = self.source.get_raw_chip(window)

        if self.rgb:
            return self.class_transformer.rgb_to_class(img)
        else:
            labels = img[:, :, 0].reshape(img.shape[0], img.shape[1])
            return labels
