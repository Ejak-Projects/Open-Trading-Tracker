import QtQuick

TextEdit {
    readOnly: true
    selectByMouse: true
    color: palette.text
    selectionColor: window.colBlue || "#2196F3"
    selectedTextColor: palette.base
    verticalAlignment: TextEdit.AlignVCenter
}
