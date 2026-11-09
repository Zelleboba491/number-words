import tkinter as tk
from tkinter import messagebox

# ---------------------------------------------------------------------------
# Словари числительных
# ---------------------------------------------------------------------------

ZERO = {"ноль": 0}

UNITS = {
    "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5,
    "шесть": 6, "семь": 7, "восемь": 8, "девять": 9,
}

TEEN = {  # 10..19 — далее по грамматике не может идти ничего
    "десять": 10, "одиннадцать": 11, "двенадцать": 12, "тринадцать": 13,
    "четырнадцать": 14, "пятнадцать": 15, "шестнадцать": 16,
    "семнадцать": 17, "восемнадцать": 18, "девятнадцать": 19,
}

TENS = {
    "двадцать": 20, "тридцать": 30, "сорок": 40, "пятьдесят": 50,
    "шестьдесят": 60, "семьдесят": 70, "восемьдесят": 80, "девяносто": 90,
}

HUNDREDS = {
    "сто": 100, "двести": 200, "триста": 300, "четыреста": 400,
    "пятьсот": 500, "шестьсот": 600, "семьсот": 700, "восемьсот": 800,
    "девятьсот": 900,
}

# Человекочитаемые названия категорий — используются в текстах ошибок,
# формулировки подогнаны под образцы с фото ("После единиц(...) не могут
# идти десятки(...)!" и т. п.)
CAT_NAME = {
    "Z": "ноль",
    "U": "единицы",
    "T": "чисел '11-19'",
    "D": "десятки",
    "H": "сотни",
}


def classify(word):
    """Определяет категорию слова и его числовое значение."""
    if word in ZERO:
        return "Z", ZERO[word]
    if word in UNITS:
        return "U", UNITS[word]
    if word in TEEN:
        return "T", TEEN[word]
    if word in TENS:
        return "D", TENS[word]
    if word in HUNDREDS:
        return "H", HUNDREDS[word]
    return None, None


def parse(text):
    """
    Разбирает строку text.
    Возвращает (число, None) при успехе или (None, текст_ошибки) при ошибке.
    """
    words = text.strip().lower().split()
    if not words:
        return None, "Введите число словами!"

    parsed = []
    for i, w in enumerate(words, start=1):
        cat, val = classify(w)
        if cat is None:
            return None, f"Во {i} слове({w}) ошибка!"
        parsed.append((cat, val, w))

    n = len(parsed)
    idx = 0

    # "ноль" — только одно слово во всём предложении
    if parsed[0][0] == "Z":
        if n > 1:
            nxt = parsed[1]
            return None, f"После нуля(ноль) не могут идти {CAT_NAME[nxt[0]]}({nxt[2]})!"
        return 0, None

    total = 0

    # 1) необязательные сотни
    if idx < n and parsed[idx][0] == "H":
        total += parsed[idx][1]
        idx += 1

    if idx >= n:
        if total == 0:
            return None, "Не удалось распознать число."
        return total, None

    cat, val, word = parsed[idx]

    # 2) число 11..19 — обязательно последнее слово
    if cat == "T":
        total += val
        idx += 1
        if idx < n:
            nxt = parsed[idx]
            return None, (f"После {CAT_NAME['T']}({word}) не могут идти "
                           f"{CAT_NAME[nxt[0]]}({nxt[2]})!")
        return total, None

    # 3) десятки, за которыми не обязательно следуют единицы
    if cat == "D":
        total += val
        idx += 1
        if idx < n:
            nxt_cat, nxt_val, nxt_word = parsed[idx]
            if nxt_cat == "U":
                total += nxt_val
                idx += 1
                if idx < n:
                    nxt2 = parsed[idx]
                    return None, (f"После единиц({nxt_word}) не могут идти "
                                   f"{CAT_NAME[nxt2[0]]}({nxt2[2]})!")
            else:
                return None, (f"После десятков({word}) не могут идти "
                               f"{CAT_NAME[nxt_cat]}({nxt_word})!")
        return total, None

    # 4) отдельные единицы — обязательно последнее слово
    if cat == "U":
        total += val
        idx += 1
        if idx < n:
            nxt = parsed[idx]
            return None, (f"После единиц({word}) не могут идти "
                           f"{CAT_NAME[nxt[0]]}({nxt[2]})!")
        return total, None

    # 5) любая другая категория здесь (H второй раз, Z не первым и т.п.)
    return None, (f"После {CAT_NAME[parsed[idx-1][0]]}({parsed[idx-1][2]}) "
                   f"не могут идти {CAT_NAME[cat]}({word})!")


# ---------------------------------------------------------------------------
# Графический интерфейс
# ---------------------------------------------------------------------------

def center_window(root, width, height):
    """Ставит окно по центру экрана при запуске."""
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


def build_gui():
    root = tk.Tk()
    root.title("БИСО-02-24 Смирнов. Число словами -> цифры")

    width, height = 420, 180
    center_window(root, width, height)   # окно появляется по центру экрана
    root.minsize(320, 150)                # разумный минимум при уменьшении
    root.resizable(True, True)            # можно расширять/уменьшать
    # окно и так можно двигать мышью за заголовок — это поведение ОС/оконного
    # менеджера, resizable(False, False) на это не влияло

    tk.Label(root, text="Число словами:").pack(anchor="w", padx=10, pady=(12, 0))
    entry_words = tk.Entry(root)
    entry_words.pack(padx=10, pady=4, fill=tk.X)

    tk.Label(root, text="Число арабскими цифрами:").pack(anchor="w", padx=10, pady=(10, 0))
    entry_number = tk.Entry(root, state="readonly")
    entry_number.pack(padx=10, pady=4, fill=tk.X)

    # -- вставка из буфера обмена (Ctrl+V и ПКМ) --------------------------
    def paste_from_clipboard(entry):
        try:
            entry.event_generate("<<Paste>>")
        except tk.TclError:
            pass
        return "break"

    def on_control_keypress(event):
        # 86 — код физической клавиши "V" (Windows VK_KEY_V). Проверяем
        # именно код клавиши, а не keysym: при русской раскладке клавиатуры
        # Ctrl+V даёт другой keysym, и стандартная вставка в Tkinter не
        # срабатывает. Код клавиши от раскладки не зависит.
        if event.keycode == 86:
            return paste_from_clipboard(entry_words)

    entry_words.bind("<Control-KeyPress>", on_control_keypress)

    def show_context_menu(event):
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="Вставить", command=lambda: paste_from_clipboard(entry_words))
        menu.tk_popup(event.x_root, event.y_root)

    entry_words.bind("<Button-3>", show_context_menu)

    def set_number(text):
        entry_number.configure(state="normal")
        entry_number.delete(0, tk.END)
        entry_number.insert(0, text)
        entry_number.configure(state="readonly")

    def on_translate(event=None):
        value, err = parse(entry_words.get())
        if err:
            set_number("0")
            messagebox.showerror("Ошибка", err)
        else:
            set_number(str(value))

    # перевод по нажатию Enter, когда фокус в поле ввода
    entry_words.bind("<Return>", on_translate)

    # -- меню по клавише F1: "О программе" и "Горячие клавиши" -----------
    def show_about():
        messagebox.showinfo(
            "О программе",
            "Число словами -> цифры\n\n"
            "Автор: Смирнов Л.Д., гр. БИСО-02-24\n\n"
            "Программа принимает число от 0 до 999, записанное словами на "
            "русском языке (например, «семьсот двадцать три»), и переводит "
            "его в арабские цифры. Ввод разбирается по словам и проверяется "
            "на правильный порядок (сотни -> десятки/число 11-19 -> "
            "единицы). Если порядок слов нарушен или слово не распознано, "
            "выводится сообщение об ошибке с указанием конкретного слова "
            "и причины."
        )

    def show_hotkeys():
        messagebox.showinfo(
            "Горячие клавиши",
            "Enter — перевести число из поля ввода\n"
            "Ctrl+V — вставить текст из буфера обмена в поле ввода\n"
            "ПКМ по полю ввода — вставить через контекстное меню\n"
            "F1 — открыть это меню (о программе / горячие клавиши)"
        )

    def show_help_menu(event=None):
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="О программе", command=show_about)
        menu.add_command(label="Горячие клавиши", command=show_hotkeys)
        x = root.winfo_pointerx()
        y = root.winfo_pointery()
        menu.tk_popup(x, y)

    root.bind("<F1>", show_help_menu)

    tk.Button(root, text="Перевести", width=15, command=on_translate).pack(pady=14)

    root.mainloop()


if __name__ == "__main__":
    build_gui()