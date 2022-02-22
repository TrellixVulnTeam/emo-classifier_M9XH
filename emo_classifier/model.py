from typing import BinaryIO, Union
from importlib import resources
from abc import ABC, abstractmethod
from pathlib import Path
from shutil import rmtree

import numpy as np
import pandas as pd

from emo_classifier import ARTIFACT_DIR
from emo_classifier.api import Comment, Prediction
from emo_classifier.emotion import load_emotions
from emo_classifier.metrics import Thresholds


class Model(ABC):
    """
    An abstract class for a model class. This provides a united interface for
    - saving a model under ARTIFACT_DIR,
    - loading a model and
    - making a prediction (for REST API)
    """

    artifact_file_name = "model.model"
    emotions: list[str] = load_emotions()

    @classmethod
    @abstractmethod
    def load_artifact_file(cls, fp: BinaryIO) -> "Model":
        """
        Given the file-like object of the model artifact, this method must recover the original Model instance.

        :param fp: file-like object of the model artifact
        :return: recovered Model instance
        """
        raise NotImplementedError

    @classmethod
    def load(cls) -> "Model":
        with resources.open_binary("emo_classifier.artifact", cls.artifact_file_name) as fp:
            model = cls.load_artifact_file(fp)
        print(f"LOADED: {type(model).__name__} instance")
        return model

    def _initialize_artifact_dir(self):
        """
        Initialize the artifact directory.
        """
        if ARTIFACT_DIR.exists():
            for file in ARTIFACT_DIR.iterdir():
                if file.is_dir():
                    rmtree(file)
                else:
                    file.unlink()
        else:
            ARTIFACT_DIR.mkdir()
        (ARTIFACT_DIR / "__init__.py").touch()

    @abstractmethod
    def save_artifact_file(self, path: Path):
        """
        Save the artifacts which we can recover the original instance from.

        :param path: save location (provided by the method save())
        """
        raise NotImplementedError

    def save(self):
        self._initialize_artifact_dir()
        file_path = ARTIFACT_DIR / self.artifact_file_name
        self.save_artifact_file(file_path)
        print("SAVED:", file_path.absolute())

    @property
    @abstractmethod
    def thresholds(self) -> Thresholds:
        raise NotImplementedError

    @thresholds.setter
    @abstractmethod
    def thresholds(self, thresholds: Thresholds):
        raise NotImplementedError

    @abstractmethod
    def predict(self, comment: Comment) -> Prediction:
        """
        Makes a prediction for a single Comment instance. This is the main functionality of the API.

        :param comment: Comment instance
        :return: Prediction instance
        """
        raise NotImplementedError

    @abstractmethod
    def predict_proba(self, X: Union[pd.Series, np.ndarray]) -> np.ndarray:
        """
        :param X: Series of texts
        :return: array of prediction of shape (#instances, #emotions)
        """
        raise NotImplementedError
