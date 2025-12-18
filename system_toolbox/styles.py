
# Color Palette - Light Mode Optimized
THEME = {
    "background": "#f8f9fa", # Slightly off-white for less glare
    "surface": "#ffffff",
    "text": "#212529",
    "text_secondary": "#6c757d",
    "border": "#dee2e6",
    "primary": "#0d6efd", # Bootstrap Primary Blue
    "primary_hover": "#0b5ed7",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "success": "#198754",
    "table_alt": "#f8f9fa",
    "header": "#ffffff",
    "selection": "#e7f1ff"
}

def get_stylesheet():
    colors = THEME
    
    return f"""
    QMainWindow, QWidget {{
        background-color: {colors['background']};
        color: {colors['text']};
        font-family: "Segoe UI", "Roboto", "Helvetica Neue", sans-serif;
        font-size: 11pt; /* Balanced font size */
    }}

    /* Tabs */
    QTabWidget::pane {{
        border: 1px solid {colors['border']};
        background: {colors['surface']};
        border-radius: 8px;
        top: -1px; 
    }}
    QTabBar::tab {{
        background: {colors['background']};
        border: none;
        padding: 12px 24px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        color: {colors['text_secondary']};
        font-size: 11pt;
        font-weight: 600;
    }}
    QTabBar::tab:selected {{
        background: {colors['surface']};
        color: {colors['primary']};
        font-weight: bold;
        border-bottom: 3px solid {colors['primary']};
    }}
    QTabBar::tab:hover {{
        background: {colors['surface']};
        color: {colors['text']};
    }}

    /* Tables */
    QTableWidget {{
        background-color: {colors['surface']};
        alternate-background-color: {colors['table_alt']};
        gridline-color: {colors['border']};
        border: 1px solid {colors['border']};
        border-radius: 6px;
        selection-background-color: {colors['selection']};
        selection-color: {colors['text']}; /* Keep text dark on light selection */
        font-size: 11pt;
        outline: none; /* Remove focus dotted line */
    }}
    QHeaderView::section {{
        background-color: {colors['header']};
        padding: 12px;
        border: none;
        border-bottom: 2px solid {colors['border']};
        font-weight: 700;
        color: {colors['text_secondary']};
        text-transform: uppercase;
        font-size: 10pt;
        letter-spacing: 0.5px;
    }}

    /* Inputs */
    QLineEdit {{
        padding: 10px;
        border: 1px solid {colors['border']};
        border-radius: 6px;
        background-color: {colors['surface']};
        color: {colors['text']};
        font-size: 11pt;
    }}
    QLineEdit:focus {{
        border: 2px solid {colors['primary']};
    }}
    
    QComboBox {{
        padding: 8px;
        border: 1px solid {colors['border']};
        border-radius: 6px;
        background-color: {colors['surface']};
        color: {colors['text']};
        font-size: 11pt;
    }}
    QComboBox::drop-down {{
        border: none;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        padding: 10px 20px;
        border-radius: 6px;
        color: {colors['text']};
        font-size: 11pt;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: #f1f3f5;
        border-color: {colors['text_secondary']};
    }}
    QPushButton:pressed {{
        background-color: {colors['border']};
    }}
    
    /* Primary Button Style */
    QPushButton#primaryBtn {{
        background-color: {colors['primary']};
        color: white;
        border: none;
    }}
    QPushButton#primaryBtn:hover {{
        background-color: {colors['primary_hover']};
    }}
    
    /* Danger Button Style */
    QPushButton#dangerBtn {{
        background-color: {colors['danger']};
        color: white;
        border: none;
    }}
    QPushButton#dangerBtn:hover {{
        background-color: #bb2d3b;
    }}

    /* Frames & Containers */
    QFrame {{
        border: none;
    }}
    QFrame#summaryFrame {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 20px;
    }}

    /* Labels */
    QLabel {{
        color: {colors['text']};
    }}
    QLabel#headerLabel {{
        font-size: 20pt;
        font-weight: 800;
        color: {colors['primary']};
    }}
    QLabel#subHeaderLabel {{
        font-size: 13pt;
        font-weight: 600;
        color: {colors['text_secondary']};
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        border: none;
        background: {colors['background']};
        width: 12px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #ced4da;
        min-height: 20px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #adb5bd;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """
