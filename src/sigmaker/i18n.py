import locale
import gettext
import os

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")

_language: str = "en"


def _detect_language() -> str:
    try:
        lang, _ = locale.getdefaultlocale()
    except (ValueError, TypeError):
        return "en"
    if not lang:
        return "en"
    code = lang.split("_")[0]
    if code == "en":
        return "en"
    return lang


_language = _detect_language()

try:
    _trans = gettext.translation(
        "sigmaker", _LOCALE_DIR, languages=[_language], fallback=True
    )
except FileNotFoundError:
    _trans = gettext.NullTranslations()

_catalog = _trans

_EN: dict[str, str] = {
    "ok": "OK",
    "cancel": "Cancel",
    "continue": "Continue?",
    "continue_title": "Continue execution?",
    "continue_question": "Continue?",
    "executing": "Executing...",
    "scanning": "scanning...",
    "match_count_unavailable": "match count unavailable",
    "match_count": "%(count)d matches",
    "match_count_sofar": "%(count)d matches so far",
    "size_bytes": "%(size)d bytes",
    "sig_already": "Signature is already %(len)d bytes. Continue?",
    "operation_canceled": "Operation canceled by user\n",
    "clipboard_error": "Error setting clipboard text: %(e)s",
    "clipboard_fail": "Failed to copy to clipboard!",
    "no_sig_entered": "No signature entered!\n",
    "invalid_action": "Invalid action!\n",
    "select_range": "Select a range to copy the code!\n",
    "enter_sig": "Enter a signature",
    "enter_end_addr": "Enter end address for selection:",
    "place_cursor_fn": "Place cursor inside a function first.\n",
    "empty_sig": "Error: Empty signature\n",
    "no_xrefs": "No XREFs have been found for your address\n",
    "sig_no_match": "Signature does not match!\n",
    "unrecognized_sig": "Unrecognized signature type\n",
    "sig_error": "Error: %(msg)s\n",
    "sig_prefix": "%(prefix)s: %(fmted)s\n",
    "sig_for": "Signature for %(address)s%(func)s: %(fmted)s\n",
    "sig_result": "Signature: %(fmted)s\n",
    "sig_search_result": "Signature: %(sig)s\n",
    "match_at": "Match @ %(addr)s\n",
    "match_in": "Match @ %(addr)s in %(func)s\n",
    "top_xrefs": "Top %(top)d Signatures out of %(total)d xrefs:\n",
    "xref_sig": "XREF Signature #%(num)d @ %(addr)s%(func)s: %(sig)s\n",
    "partial_unique": "Partial signature (NOT unique, %(count_str)s)",
    "partial_unique_for": "Partial signature (NOT unique, %(count_str)s) for %(address)s%(func)s",
    "fn_sig": "Function signature (offset +%(offset)s into function %(func_start)s%(func_name)s):\n",
    "no_fn_sig": "No unique signature inside function %(func_start)s; trying xref signatures...\n",
    "xref_fallback": "Falling back to xref signatures...\n\nPress Cancel to stop",
    "xref_sig_into": "Xref signature into %(func_start)s (from %(addr)s):\n",
    "no_sig_found": "No unique signature found for function %(func_start)s (no unique sig within body and no usable xrefs)\n",
    "addr_error": "Error: End address %(end_addr)s must be greater than start address %(start_addr)s.",
    "addr_no_end": "No end address selected, using line end: %(ea)s",
    "mask_detect_fail": "Detected mask \"%(mask)s\" but failed to match corresponding bytes\n",
    "running_for": "%(func)s has been running for %(time)s.",
    "plugin_info": "%(name)s v%(version)s for IDA Pro by %(author)s",
    "plugin_help": "Select location in disassembly and press CTRL+ALT+S to open menu",
    "action.sigmaker": "SigMaker",
    "action.start_profiling": "Start Profiling",
    "action.stop_profiling": "Stop Profiling",
    "action.sigmaker_tt": "Show the signature maker dialog.",
    "action.start_profiling_tt": "Start a cProfile session capturing subsequent SigMaker activity.",
    "action.stop_profiling_tt": "Stop the active cProfile session and write the dump to the user IDA dir.",
    # Progress box
    "progress.processing_idx": "Processing (%(idx)d) | Elapsed: %(elapsed)ds",
    "progress.processing_total": "Processing (%(idx)d/%(total)d) | Elapsed: %(elapsed)ds",
    "progress.copy_segments": "Please stand by, copying segments...",
    "progress.copy_segment": "Please stand by, copying the segment...",
    "progress.copy_code": (
        "Copy selected code\n\n"
        "Building a signature for the selected address range.\n\n"
        "Press Cancel to stop"
    ),
    "progress.create_unique": (
        "Create unique signature (from cursor address)\n\n"
        "Growing a pattern from the current address until it "
        "matches exactly one place in the binary.\n\n"
        "Press Cancel to stop"
    ),
    "progress.find_fn_sig": (
        "Find shortest function signature\n\n"
        "Trying every instruction in the function as a start point; "
        "growing each until unique and keeping the shortest.\n\n"
        "Press Cancel to stop"
    ),
    "progress.search_sig": (
        "Search for a signature\n\n"
        "Scanning %(scope)s for your pattern.\n\n"
        "Press Cancel to stop"
    ),
    "progress.xref_progress": (
        "Find shortest XREF signature\n\n"
        "Processing xref %(i)d of %(total)d (%(pct).1f%%)...\n\n"
        "Suitable Signatures: %(suitable)d\n"
        "Shortest Signature: %(shortest)d Bytes"
    ),
    # Form: main
    "form.main.select_action": "Select action",
    "form.main.create_unique": "Create unique signature for current code address",
    "form.main.create_unique_tt": "Create a unique code signature for the current address",
    "form.main.find_xref": "Find shortest XREF signature for current data or code address",
    "form.main.find_xref_tt": "Create code signatures for xrefs of the selected address",
    "form.main.copy_code": "Copy selected code",
    "form.main.copy_code_tt": "Copy selected code bytes in the specified output format",
    "form.main.search_sig": "Search for a signature",
    "form.main.search_sig_tt": "Search the database for a signature pattern",
    "form.main.find_fn_sig": "Find shortest unique signature for current function",
    "form.main.find_fn_sig_tt": "Find the shortest unique signature anywhere inside the current function",
    "form.main.output_format": "Output format",
    "form.main.ida_sig": "IDA Signature",
    "form.main.ida_sig_tt": "IDA style: E8 ? ? ? ? 45 33 F6",
    "form.main.x64dbg_sig": "x64Dbg Signature",
    "form.main.x64dbg_sig_tt": "x64Dbg style: E8 ?? ?? ?? ?? 45 33 F6",
    "form.main.mask_sig": "C Byte Array String Signature + String mask",
    "form.main.mask_sig_tt": "C byte array + mask string",
    "form.main.bitmask_sig": "C Bytes Signature + Bitmask",
    "form.main.bitmask_sig_tt": "C byte array + bitmask",
    "form.main.quick_options": "Quick Options",
    "form.main.wildcards": "Wildcards for operands",
    "form.main.wildcards_tt": "Wildcard operands to improve signature stability",
    "form.main.continue_outside": "Continue when leaving function scope",
    "form.main.continue_outside_tt": "Don't stop at function boundary",
    "form.main.wildcard_opt": "Wildcard optimized / combined instructions",
    "form.main.wildcard_opt_tt": "Wildcard combined instructions",
    "form.main.enable_prompt": "Enable continue prompt (opt-in)",
    "form.main.enable_prompt_tt": "Show periodic 'Continue?' prompts",
    "form.main.partial_on_cancel": "Output partial signature on cancel (opt-in)",
    "form.main.partial_on_cancel_tt": "Output partial signature on cancel",
    "form.main.scope_to_segment": "Limit uniqueness and search to the containing segment (opt-in)",
    "form.main.scope_to_segment_tt": "Scope uniqueness/search to containing segment",
    "form.main.operand_types": "Operand types...",
    "form.main.other_options": "Other options...",
    # Form: options
    "form.options.title": "Options",
    "form.options.top_x_tt": "Maximum number of shortest XREF signatures to display",
    "form.options.top_x": "Print top X XREF signatures",
    "form.options.max_single_tt": "Maximum length of a single signature in bytes",
    "form.options.max_single": "Maximum single signature length",
    "form.options.max_xref_tt": "Maximum length of an XREF signature in bytes",
    "form.options.max_xref": "Maximum xref signature length",
    "form.options.prompt_interval_tt": "Seconds before the first 'Continue?' prompt. -1 disables the prompt.",
    "form.options.prompt_interval": "Prompt interval (seconds, -1 disables)",
    # Form: operand types
    "form.operand.title": "Wildcardable Operands",
    "form.operand.select_hint": "Select operand types that should be wildcarded:",
    "form.operand.general_reg": "General Register (al, ax, es, ds...)",
    "form.operand.mem_ref": "Direct Memory Reference (DATA)",
    "form.operand.phrase": "Memory Ref [Base Reg + Index Reg]",
    "form.operand.displ": "Memory Ref [Base Reg + Index Reg + Displacement]",
    "form.operand.imm": "Immediate Value",
    "form.operand.far": "Immediate Far Address (CODE)",
    "form.operand.near": "Immediate Near Address (CODE)",
    "form.operand.trace_reg": "Trace Register",
    "form.operand.debug_reg": "Debug Register",
    "form.operand.control_reg": "Control Register",
    "form.operand.fp_reg": "Floating Point Register",
    "form.operand.mmx_reg": "MMX Register",
    "form.operand.xmm_reg": "XMM Register",
    "form.operand.ymm_reg": "YMM Register",
    "form.operand.zmm_reg": "ZMM Register",
    "form.operand.opmask_reg": "Opmask Register",
    "form.operand.unused": "(Unused)",
    "form.operand.reg_list": "Register list (for LDM/STM)",
    "form.operand.coproc_list": "Coprocessor register list (for CDP)",
    "form.operand.coproc_reg": "Coprocessor register (for LDC/STC)",
    "form.operand.fp_list": "Floating point register list",
    "form.operand.arbitrary_text": "Arbitrary text stored in the operand",
    "form.operand.arm_cond": "ARM condition as an operand",
    "form.operand.spr": "Special purpose register",
    "form.operand.two_fpr": "Two FPRs",
    "form.operand.sh_mb_me": "SH & MB & ME",
    "form.operand.crfield": "crfield",
    "form.operand.crbit": "crbit",
    "form.operand.dcr": "Device control register",
    # Progress templates (assembled in code, these are the format strings)
    "progress.unique_sig_detail": (
        "Create unique signature (from cursor address)\n"
        "Growing a pattern from the current address until it matches\n"
        "exactly one place in the binary.\n\n"
        "Length:  %(length)s bytes\n"
        "Matches: %(matches)s\n"
        "Elapsed: %(elapsed)s\n\n"
        "Press Cancel to stop"
    ),
    "progress.fn_sig_detail": (
        "Find shortest function signature\n"
        "Trying every instruction as a start point; "
        "keeping the shortest unique one.\n"
        "\n"
        "Function:     %(fn_bounds)s  (%(fn_size)d bytes)\n"
        "Anchor (#%(idx)d): %(anchor)s\n"
        "Inner search: %(inner_bounds)s  (%(inner_length)d bytes, "
        "%(inner_matches_str)s)\n"
        "Best found:   %(best)s\n"
        "Candidates:   %(candidates_count)d unique so far\n"
        "Elapsed:      %(elapsed)d\n"
        "\n"
        "Press Cancel to stop"
    ),
}


def t(key: str) -> str:
    r = _catalog.gettext(key)
    if r and r != key:
        return r
    return _EN.get(key, key)


_ = t


def get_language() -> str:
    return _language
