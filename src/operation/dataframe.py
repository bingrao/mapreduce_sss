# WS client example
from src.operation.op import AbstractOperation
import asyncio
import websockets
from src.share.secret_share import SecretShare
from src.event.event import MessageEvent
from src.event.message import DataMessage, ControlMessage
from src.utils.embedding import Embedding
from functools import partial
import numpy as np
import time


class DataFrameComputation(AbstractOperation):
    def __init__(self, ctx, poly_order=1):
        super(DataFrameComputation, self).__init__(ctx, poly_order)
