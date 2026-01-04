import os
import math
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.text import LabelBase
from kivy.utils import platform

# --- 文字化け対策: フォントパスの厳格化 ---
# Androidの内部ストレージ上のパスを確実に取得します
if platform == 'android':
    base_path = os.environ.get('PYTHONPATH', '.')
    if ':' in base_path:
        base_path = base_path.split(':')[0]
else:
    base_path = os.path.dirname(__file__)

JAPANESE_FONT = os.path.join(base_path, "fonts", "NotoSansJP-Regular.otf")

# フォント登録 (Robotoを上書きして全体を日本語化)
LabelBase.register(name="Roboto", fn_regular=JAPANESE_FONT)
LabelBase.register(name="Japanese", fn_regular=JAPANESE_FONT)

class MainMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding=40, spacing=30)
        layout.add_widget(MDLabel(
            text="PRO-MECHANIC SUITE", halign="center", font_style="H4"
        ))
        layout.add_widget(MDRaisedButton(
            text="油圧シリンダー推力計算", pos_hint={'center_x': 0.5}, size_hint_x=0.9,
            on_release=lambda x: setattr(self.manager, 'current', 'cylinder')
        ))
        layout.add_widget(MDBoxLayout())
        self.add_widget(layout)

class CylinderScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', spacing=15, padding=30)
        
        self.bore = MDTextField(hint_text="シリンダー内径 D (mm)", input_filter="float", mode="rectangle")
        self.rod = MDTextField(hint_text="ロッド直径 d (mm)", input_filter="float", mode="rectangle")
        self.pressure = MDTextField(hint_text="リリーフ圧力 P (MPa)", input_filter="float", mode="rectangle")
        
        layout.add_widget(self.bore)
        layout.add_widget(self.rod)
        layout.add_widget(self.pressure)
        
        self.result_label = MDLabel(text="結果がここに表示されます", halign="left", font_style="Body1", theme_text_color="Secondary")
        layout.add_widget(self.result_label)

        layout.add_widget(MDRaisedButton(text="計算実行", pos_hint={'center_x': 0.5}, on_release=self.calculate))
        layout.add_widget(MDRectangleFlatButton(text="戻る", pos_hint={'center_x': 0.5}, on_release=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(layout)

    def calculate(self, *args):
        try:
            D = float(self.bore.text)
            d = float(self.rod.text)
            P = float(self.pressure.text)
            
            # 受圧面積 (cm2)
            A_push = (math.pi * (D/10)**2) / 4
            A_pull = (math.pi * ((D/10)**2 - (d/10)**2)) / 4
            
            # 推力 (ton) : 1MPa = 10.197 kgf/cm2
            F_push = (A_push * P * 10.197) / 1000
            F_pull = (A_pull * P * 10.197) / 1000
            
            self.result_label.text = (
                f"【計算式】\n"
                f"面積(押し): (π×{D/10:.1f}²)/4 = {A_push:.2f} cm²\n"
                f"面積(引き): (π×({D/10:.1f}²-{d/10:.1f}²))/4 = {A_pull:.2f} cm²\n"
                f"推力: 面積(cm²) × 圧力(MPa) × 10.197\n"
                f"※10.197はMPaからkgf/cm²への換算係数\n\n"
                f"▶ 押し出力: {F_push:.2f} ton\n"
                f"▶ 引き出力: {F_pull:.2f} ton"
            )
        except:
            self.result_label.text = "数値を正しく入力してください"

class ProMechanicApp(MDApp):
    def build(self):
        # build内ではテーマ設定のみ
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        
        # デフォルトフォントを「Japanese」に指定
        self.theme_cls.font_styles["H4"] = ["Japanese", 30, False, 0.15]
        self.theme_cls.font_styles["Body1"] = ["Japanese", 16, False, 0.15]
        self.theme_cls.font_styles["Button"] = ["Japanese", 14, True, 0.15]

        sm = MDScreenManager()
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(CylinderScreen(name='cylinder'))
        return sm

    def on_start(self):
        # アプリ起動時に、全てのMDLabelなどのベースとなるフォントを上書き
        from kivy.core.text import LabelBase
        # フォントファイルの存在チェックをログに出す（adbで確認するため）
        if os.path.exists(JAPANESE_FONT):
            print(f"DEBUG: Font found at {JAPANESE_FONT}")
        else:
            print(f"DEBUG: Font NOT FOUND at {JAPANESE_FONT}")

if __name__ == "__main__":
    ProMechanicApp().run()
