import os
import sys
import math
import webbrowser
import subprocess
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.text import LabelBase

# 実行ファイルのディレクトリを取得
if getattr(sys, 'frozen', False):
    # アプリとして固められている場合
    base_path = sys._MEIPASS
else:
    # 通常の実行時
    base_path = os.path.dirname(os.path.abspath(__file__))

# フォントパスを相対的に指定
JAPANESE_FONT = os.path.join(base_path, "fonts", "NotoSansJP-Regular.otf")

# Kivyに登録
LabelBase.register(name="Roboto", fn_regular=JAPANESE_FONT)
LabelBase.register(name="Japanese", fn_regular=JAPANESE_FONT)

class MainMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding=40, spacing=30)

        layout.add_widget(MDLabel(
            text="PRO-MECHANIC SUITE",
            halign="center",
            font_style="H4",
            theme_text_color="Primary"
        ))
        
        layout.add_widget(MDLabel(
            text="建設機械エンジニア向け測定・診断アプリ",
            halign="center",
            font_style="Subtitle2",
            theme_text_color="Secondary"
        ))

        layout.add_widget(MDRaisedButton(
            text="油圧シリンダー推力計算 (Cylinder Calc)",
            pos_hint={'center_x': 0.5},
            size_hint_x=0.9,
            on_release=self.go_to_cylinder
        ))
        
        layout.add_widget(MDRectangleFlatButton(
            text="エンジン診断 (Coming Soon)",
            pos_hint={'center_x': 0.5},
            size_hint_x=0.9,
            disabled=True
        ))

        layout.add_widget(MDBoxLayout()) 

        # フッター
        footer = MDRectangleFlatButton(
            text="go-pro-world.net since 2025",
            pos_hint={'center_x': 0.5},
            on_release=self.open_link
        )
        layout.add_widget(footer)
        self.add_widget(layout)

    def go_to_cylinder(self, *args):
        self.manager.current = 'cylinder'

    def open_link(self, *args):
        import webbrowser
        url = "http://go-pro-world.net"
        
        # 複雑なパス指定をせず、標準ライブラリに任せるのが一番安全です
        # WSL環境では、これにより Windows側のブラウザが開きます
        webbrowser.open(url)

class CylinderScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', spacing=15, padding=30, pos_hint={'top': 1})

        layout.add_widget(MDLabel(text="油圧シリンダー推力計算", halign="center", font_style="H6", size_hint_y=None, height="40dp"))

        self.bore = MDTextField(hint_text="シリンダー内径 (mm)", input_filter="float", mode="rectangle")
        self.rod = MDTextField(hint_text="ロッド直径 (mm)", input_filter="float", mode="rectangle")
        self.pressure = MDTextField(hint_text="リリーフ圧力 (MPa)", input_filter="float", mode="rectangle")
        
        layout.add_widget(self.bore)
        layout.add_widget(self.rod)
        layout.add_widget(self.pressure)

        layout.add_widget(MDRaisedButton(text="推力を計算", pos_hint={'center_x': 0.5}, on_release=self.calculate, size_hint_x=0.8))

        # 結果表示（多行表示に対応）
        self.result_label = MDLabel(
            text="数値を入力してください", 
            halign="left", 
            font_style="Body2",
            theme_text_color="Primary",
            line_height=1.2
        )
        layout.add_widget(self.result_label)

        layout.add_widget(MDRectangleFlatButton(text="メニューに戻る", pos_hint={'center_x': 0.5}, on_release=self.back))
        self.add_widget(layout)

    def back(self, *args):
        self.manager.current = 'menu'

    def calculate(self, instance):
        try:
            D = float(self.bore.text) # 内径 mm
            d = float(self.rod.text)  # ロッド径 mm
            P = float(self.pressure.text) # 圧力 MPa

            # 受圧面積計算 (cm^2換算)
            A_push = (math.pi * (D**2)) / 400
            A_pull = (math.pi * (D**2 - d**2)) / 400

            # 推力計算 (ton)
            # F = (P * A * 10.197) / 1000  または (P * A * 100) / 9806.65
            F_push = (P * A_push * 100) / 9.80665 / 1000
            F_pull = (P * A_pull * 100) / 9.80665 / 1000

            self.result_label.text = (
                f"【計算プロセス】\n"
                f"1. 押し面積: (π × {D/10:.1f}²) / 4 = {A_push:.2f} cm²\n"
                f"2. 引き面積: π × ({D/10:.1f}² - {d/10:.1f}²) / 4 = {A_pull:.2f} cm²\n"
                f"3. 換算係数: 1 MPa ≈ 10.197 kgf/cm²\n\n"
                f"【計算結果】\n"
                f"▶ 押し出力: {F_push:.2f} ton\n"
                f"▶ 引き出力: {F_pull:.2f} ton"
            )
        except Exception:
            self.result_label.text = "エラー: 正しい数値を入力してください"

class ProMechanicApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        
        self.theme_cls.font_styles.update({
            "H4": ["Japanese", 30, False, 0.15],
            "H6": ["Japanese", 20, False, 0.15],
            "Subtitle2": ["Japanese", 14, False, 0.15],
            "Body2": ["Japanese", 13, False, 0.15],
            "Button": ["Japanese", 14, True, 0.15],
        })

        sm = MDScreenManager()
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(CylinderScreen(name='cylinder'))
        return sm

if __name__ == "__main__":
    ProMechanicApp().run()
