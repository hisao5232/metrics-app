import os
import math
import webbrowser
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

# メインメニュー画面
class MainMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding=[40, 40, 40, 20], spacing=20)
        
        layout.add_widget(MDLabel(
            text="PRO-MECHANIC SUITE", halign="center", font_style="H4"
        ))
        layout.add_widget(MDRaisedButton(
            text="油圧シリンダー推力計算", pos_hint={'center_x': 0.5}, size_hint_x=0.9,
            on_release=lambda x: setattr(self.manager, 'current', 'cylinder')
        ))

        layout.add_widget(MDRaisedButton(
            text="鋼材重量計算 (SS400)", pos_hint={'center_x': 0.5}, size_hint_x=0.9,
            on_release=lambda x: setattr(self.manager, 'current', 'steel')
        ))

        # スペーサー（これを入れることでサイトリンクが一番下に押し下げられます）
        layout.add_widget(MDBoxLayout())

        # 独自ドメインへのリンクボタンを復活
        layout.add_widget(MDRectangleFlatButton(
            text="go-pro-world.net", 
            pos_hint={'center_x': 0.5},
            on_release=lambda x: webbrowser.open("http://go-pro-world.net")
        ))

        self.add_widget(layout)

# 油圧シリンダー推力計算画面
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

    # 計算実行ボタンを押した時の処理
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

# 鋼材重量計算画面
class SteelScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', spacing=15, padding=30)
        
        layout.add_widget(MDLabel(text="鋼材重量計算 (SS400)", halign="center", font_style="H6"))
        
        self.input_w = MDTextField(hint_text="幅 W (mm)", input_filter="float", mode="rectangle")
        self.input_l = MDTextField(hint_text="長さ L (mm)", input_filter="float", mode="rectangle")
        self.input_t = MDTextField(hint_text="厚み T (mm)", input_filter="float", mode="rectangle")
        
        layout.add_widget(self.input_w)
        layout.add_widget(self.input_l)
        layout.add_widget(self.input_t)
        
        self.result_label = MDLabel(text="寸法を入力してください", halign="left", font_style="Body2")
        layout.add_widget(self.result_label)
        
        layout.add_widget(MDRaisedButton(text="重量計算", pos_hint={'center_x': 0.5}, on_release=self.calculate))
        layout.add_widget(MDRectangleFlatButton(text="戻る", pos_hint={'center_x': 0.5}, on_release=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(layout)

    # 重量計算ボタンを押した時の処理
    def calculate(self, *args):
        try:
            w = float(self.input_w.text)
            l = float(self.input_l.text)
            t = float(self.input_t.text)
            
            # cm単位に変換して体積(cm3)を出す
            volume = (w / 10) * (l / 10) * (t / 10)
            # 比重 7.85g/cm3 を掛けて重量(g)を出し、kgに変換
            weight = (volume * 7.85) / 1000
            
            self.result_label.text = (
                f"【計算式】\n"
                f"体積: {w/10:.1f} × {l/10:.1f} × {t/10:.1f} = {volume:.2f} cm³\n"
                f"重量: {volume:.2f} cm³ × 7.85(比重) ÷ 1000\n\n"
                f"▶ 重量: {weight:.3f} kg"
            )
        except:
            self.result_label.text = "数値を正しく入力してください"

# アプリクラス フォント　背景
class ProMechanicApp(MDApp):
    def build(self):
        # build内ではテーマ設定のみ
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        
        # 既存のフォントスタイル設定をループで回して、全て "Japanese" に変更します
        font_name = "Japanese"
        for style in self.theme_cls.font_styles:
            # 各スタイルの[フォント名, サイズ, 太字フラグ, スペーシング]のリストを更新
            if style in self.theme_cls.font_styles:
                self.theme_cls.font_styles[style][0] = font_name

        sm = MDScreenManager()
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(CylinderScreen(name='cylinder'))
        sm.add_widget(SteelScreen(name='steel'))
        return sm

# アプリ起動時の処理
    def on_start(self):
        # アプリ起動時に、全てのMDLabelなどのベースとなるフォントを上書き
        from kivy.core.text import LabelBase
        # フォントファイルの存在チェックをログに出す（adbで確認するため）
        if os.path.exists(JAPANESE_FONT):
            print(f"DEBUG: Font found at {JAPANESE_FONT}")
        else:
            print(f"DEBUG: Font NOT FOUND at {JAPANESE_FONT}")

# アプリ起動
if __name__ == "__main__":
    ProMechanicApp().run()
