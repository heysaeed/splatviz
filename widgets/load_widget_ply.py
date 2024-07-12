# SPDX-FileCopyrightText: Copyright (c) 2021-2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import os
from imgui_bundle import imgui
from gui_utils import imgui_utils


class LoadWidget:
    def __init__(self, viz, root):
        self.viz = viz
        self.root = root
        self.filter = ""
        self.items = self.list_runs_and_pkls()
        if len(self.items) == 0:
            raise FileNotFoundError(f"No .ply or compression_config.yml found in '{root}' with filter 'f{self.filter}'")
        self.plys: list[str] = [self.items[-1]]
        self.use_splitscreen = False
        self.highlight_border = False

    @imgui_utils.scoped_by_object_id
    def __call__(self, show=True):
        viz = self.viz
        if show:
            _changed, self.filter = imgui.input_text("Filter", self.filter)

            for i, ply in enumerate(self.plys):
                if imgui.begin_popup(f"browse_pkls_popup{i}"):
                    for item in self.items:
                        clicked = imgui.menu_item_simple(os.path.relpath(item, self.root))
                        if clicked:
                            self.plys[i] = item
                    imgui.end_popup()

                if imgui_utils.button(f"Browse {i + 1}", width=viz.button_w):
                    imgui.open_popup(f"browse_pkls_popup{i}")
                    self.items = self.list_runs_and_pkls()
                imgui.same_line()
                imgui.text(f"Scene {i + 1}: " + ply[len(self.root):])

            if imgui_utils.button("Add Scene"):
                self.plys.append(self.plys[-1])

            use_splitscreen, self.use_splitscreen = imgui.checkbox("Splitscreen", self.use_splitscreen)
            highlight_border, self.highlight_border = imgui.checkbox("Highlight Border", self.highlight_border)

        viz.args.highlight_border = self.highlight_border
        viz.args.use_splitscreen = self.use_splitscreen
        viz.args.ply_file_paths = self.plys
        viz.args.current_ply_names = [ply[0].replace("/", "_").replace("\\", "_").replace(":", "_").replace(".", "_") for ply in self.plys]

    def list_runs_and_pkls(self) -> list[str]:
        self.items = []
        for root, dirs, files in os.walk(self.root):
            for file in files:
                if file.endswith(".ply") or file.endswith("compression_config.yml"):
                    current_path = os.path.join(root, file)
                    if all([filter in current_path for filter in self.filter.split(",")]):
                        self.items.append(str(current_path))
        return self.items