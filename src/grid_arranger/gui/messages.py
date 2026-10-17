"""Lokalizované hlášky ze stabilních kódů chyb a upozornění (spec. kap. 36.4).

Jádro a adaptér vracejí jen kód a parametry; text vzniká až zde.
Zdrojové texty jsou anglicky, překlady v ``translations/gridarranger_*.ts``.
"""

from __future__ import annotations

from PySide6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication

CTX = "Messages"

TEMPLATES: dict[str, str] = {
    # projekt / soubor
    "legacy_format": QT_TRANSLATE_NOOP("Messages", "This application supports only .lbrn2 projects. Save the project in LightBurn as .lbrn2."),
    "not_lbrn2": QT_TRANSLATE_NOOP("Messages", "The file is not a .lbrn2 project."),
    "file_too_large": QT_TRANSLATE_NOOP("Messages", "The file is too large."),
    "xml_malformed": QT_TRANSLATE_NOOP("Messages", "The file is damaged or is not a valid LightBurn project."),
    "xml_encoding": QT_TRANSLATE_NOOP("Messages", "Unsupported text encoding (only UTF-8 is supported)."),
    "xml_dtd_forbidden": QT_TRANSLATE_NOOP("Messages", "The file contains constructs that are refused for security reasons."),
    "not_lightburn_project": QT_TRANSLATE_NOOP("Messages", "The file is not a LightBurn project."),
    "unsupported_version": QT_TRANSLATE_NOOP("Messages", "Unsupported LightBurn version ({app_version}, format {format_version}). Supported: LightBurn 2.2."),
    "unsupported_orientation": QT_TRANSLATE_NOOP("Messages", "This laser origin ({origin}) has not been verified yet. Supported: origin top left or top right."),
    "unknown_orientation": QT_TRANSLATE_NOOP("Messages", "The project has an invalid mirror setting."),
    "unknown_project_attribute": QT_TRANSLATE_NOOP("Messages", "The project contains unknown properties ({attrs}) and cannot be processed safely."),
    "multi_page_unsupported": QT_TRANSLATE_NOOP("Messages", "Projects with several pages are not supported."),
    # výrobek
    "unknown_element": QT_TRANSLATE_NOOP("Messages", "Contains unknown data that could be damaged by moving."),
    "unknown_group_attribute": QT_TRANSLATE_NOOP("Messages", "The group has unknown properties (for example locked): {attrs}."),
    "unsupported_shape_type": QT_TRANSLATE_NOOP("Messages", "Contains an unsupported object type: {type}."),
    "unknown_shape_attribute": QT_TRANSLATE_NOOP("Messages", "The shape {type} has unknown properties ({attrs}) and cannot be processed safely."),
    "unreadable_shape": QT_TRANSLATE_NOOP("Messages", "Contains a shape {type} with unreadable dimensions."),
    "bad_xform": QT_TRANSLATE_NOOP("Messages", "Contains an unreadable transformation."),
    "unreadable_path": QT_TRANSLATE_NOOP("Messages", "Contains an unreadable curve."),
    "no_outline": QT_TRANSLATE_NOOP("Messages", "No closed cut outline was found."),
    "content_outside_outline": QT_TRANSLATE_NOOP("Messages", "Some content extends beyond the cut outline."),
    "ambiguous_outline": QT_TRANSLATE_NOOP("Messages", "The cut outline is ambiguous ({count} candidates)."),
    "degenerate_outline": QT_TRANSLATE_NOOP("Messages", "The cut outline has zero size."),
    "empty_group": QT_TRANSLATE_NOOP("Messages", "The group is empty."),
    "text_backup_mismatch": QT_TRANSLATE_NOOP("Messages", "Text geometry does not match its position. Open and save the project in LightBurn again."),
    "text_unmeasurable": QT_TRANSLATE_NOOP("Messages", "Text “{text}” cannot be measured — check it in LightBurn Preview."),
    # rozložení
    "material_missing": QT_TRANSLATE_NOOP("Messages", "Enter the board size."),
    "invalid_material": QT_TRANSLATE_NOOP("Messages", "The board size is invalid."),
    "invalid_margin": QT_TRANSLATE_NOOP("Messages", "The margins are invalid."),
    "margins_exceed_material": QT_TRANSLATE_NOOP("Messages", "The margins are larger than the board."),
    "outside_material": QT_TRANSLATE_NOOP("Messages", "{a} extends beyond the usable board area."),
    "items_overlap": QT_TRANSLATE_NOOP("Messages", "{a} and {b} overlap."),
    "gap_violation": QT_TRANSLATE_NOOP("Messages", "{a} and {b} are closer than the gap."),
    "obstacle_overlap": QT_TRANSLATE_NOOP("Messages", "{a} collides with {b}, which is not being moved."),
    "obstacle_gap_violation": QT_TRANSLATE_NOOP("Messages", "{a} is too close to {b}, which is not being moved."),
    "obstacle_unmeasurable": QT_TRANSLATE_NOOP("Messages", "The size of {a} cannot be determined, so saving is blocked."),
    "zero_gap": QT_TRANSLATE_NOOP("Messages", "Zero gap: items touch each other — risky when cutting."),
    "minimum_gap_only": QT_TRANSLATE_NOOP("Messages", "Items have different sizes: the gap is a minimum, not exactly the same everywhere."),
    # parametry a úloha
    "invalid_columns": QT_TRANSLATE_NOOP("Messages", "The number of columns must be at least 1."),
    "invalid_gap": QT_TRANSLATE_NOOP("Messages", "The gap must be 0 or more."),
    "invalid_start": QT_TRANSLATE_NOOP("Messages", "Enter the grid corner position."),
    "invalid_anchor": QT_TRANSLATE_NOOP("Messages", "Unknown grid placement."),
    "invalid_fill_corner": QT_TRANSLATE_NOOP("Messages", "Unknown fill order."),
    "invalid_rotation": QT_TRANSLATE_NOOP("Messages", "Unknown rotation mode."),
    "bad_transform": QT_TRANSLATE_NOOP("Messages", "Internal error: invalid item transformation. Nothing was saved."),
    "empty_project": QT_TRANSLATE_NOOP("Messages", "The project contains no shapes."),
    "empty_selection": QT_TRANSLATE_NOOP("Messages", "Select at least one item."),
    "duplicate_item": QT_TRANSLATE_NOOP("Messages", "An item is listed more than once."),
    "unknown_item": QT_TRANSLATE_NOOP("Messages", "Unknown item."),
    "degenerate_item": QT_TRANSLATE_NOOP("Messages", "An item has zero size."),
    "internal_overlap": QT_TRANSLATE_NOOP("Messages", "Internal error: the grid calculation violated the gap. Nothing was saved."),
    "item_not_supported": QT_TRANSLATE_NOOP("Messages", "The selected item cannot be moved."),
    "validation_failed": QT_TRANSLATE_NOOP("Messages", "The layout did not pass the check; nothing was saved."),
    "verification_failed": QT_TRANSLATE_NOOP("Messages", "The output check failed; nothing was saved."),
    "source_changed": QT_TRANSLATE_NOOP("Messages", "The original file has changed since it was opened. Open it again."),
    "output_exists": QT_TRANSLATE_NOOP("Messages", "The file already exists (or its protocol .json does). The application never overwrites files; nothing was saved."),
    "would_overwrite_source": QT_TRANSLATE_NOOP("Messages", "The output would overwrite the original; refused."),
    "write_failed": QT_TRANSLATE_NOOP("Messages", "Saving failed: {detail}"),
    "no_free_output_name": QT_TRANSLATE_NOOP("Messages", "There is no free name for the output file."),
}

FALLBACK = QT_TRANSLATE_NOOP("Messages", "Error {code}")


class _Safe(dict):
    def __missing__(self, key: str) -> str:
        return "?"


def message(code: str, **params) -> str:
    tpl = TEMPLATES.get(code)
    if tpl is None:
        return QCoreApplication.translate(CTX, FALLBACK).format_map(_Safe(code=code))
    p = {k: (", ".join(map(str, v)) if isinstance(v, (list, tuple)) else v) for k, v in params.items()}
    return QCoreApplication.translate(CTX, tpl).format_map(_Safe(p))


def issue_text(code: str, item_ids: tuple[str, ...], params: dict) -> str:
    names = list(item_ids) + ["", ""]
    return message(code, a=names[0], b=names[1], **params)
