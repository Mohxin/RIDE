#  Copyright 2008-2009 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from robotide.controller.cellinfo import CellType
import wx
# this import fails in HUDSON
# from wxPython._gdi import wxFONTWEIGHT_BOLD, wxFONTWEIGHT_NORMAL
wxFONTWEIGHT_BOLD = 92
wxFONTWEIGHT_NORMAL = 90

class Colorizer(object):

    def __init__(self, grid, controller, colors):
        self._grid = grid
        self._controller = controller
        self._colors=colors

    def colorize(self, selection_content):
        wx.CallAfter(self._color_me_task, 0, 0, selection_content)

    def _color_me_task(self, row, col, selection_content):
        if row >= self._grid.NumberRows:
            self._grid.ForceRefresh()
        elif col < self._grid.NumberCols:
            self._colorize_cell(row, col, selection_content)
            wx.CallAfter(self._color_me_task, row, col+1, selection_content)
        else:
            self._color_me_task(row+1, 0, selection_content)

    def _colorize_cell(self, row, col, selection_content):
        cell_info = self._controller.get_cell_info(row, col)
        if cell_info is None:
            self._set_default_colors(row, col)
            return
        self._grid.SetCellTextColour(row, col, self._get_text_color(cell_info))
        self._grid.SetCellBackgroundColour(row, col, self._get_background_color(cell_info, selection_content))
        self._grid.SetCellFont(row, col, self._get_cell_font(row, col, cell_info))

    def _set_default_colors(self, row, col):
        self._grid.SetCellTextColour(row, col, self._colors.DEFAULT_TEXT)
        self._grid.SetCellBackgroundColour(row, col, self._colors.DEFAULT_BACKGROUND)

    def _get_text_color(self, cell_info):
        return self._colors.get_text_color(cell_info.content_type)

    def _get_background_color(self, cell_info, selection_content):
        if cell_info.matches(selection_content):
            return self._colors.get_highlight_color()
        if cell_info.has_error():
            return self._colors.get_error_color()
        return self._colors.get_background_color(cell_info.cell_type)

    def _get_cell_font(self, row, col, cell_info):
        font = self._grid.GetCellFont(row, col)
        font.SetWeight(self._get_weight(cell_info))
        return font

    def _get_weight(self, cell_info):
        if cell_info.cell_type == CellType.KEYWORD:
            return wxFONTWEIGHT_BOLD
        return wxFONTWEIGHT_NORMAL


class ColorizationSettings(object):

    DEFAULT_TEXT = 'black'
    DEFAULT_BACKGROUND = 'white'

    def __init__(self, settings=None):
        self._settings = settings

    def get_background_color(self, type):
        if not self._settings:
            return self.DEFAULT_BACKGROUND
        return self._get('background %s' % type)

    def get_text_color(self, type):
        if not self._settings:
            return self.DEFAULT_TEXT
        return self._get('text %s' % type)

    def get_highlight_color(self):
        return self.get_background_color('highlight')

    def get_error_color(self):
        return self.get_background_color('error')

    def _get(self, name):
        return self._settings['Colors'][name.lower().replace('_',' ')]
