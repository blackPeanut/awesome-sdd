#!/usr/bin/env python3
"""Plan Codex worker arguments from validated settings and observed host capabilities.

Read-only: this does not spawn workers, change a running model, or edit configuration.
The caller supplies capabilities from its live tools, never from guessed model names.
"""
import argparse
import json
from pathlib import Path
import sys

from settings import (CODEX_EFFORTS, CODEX_ROLES, SettingsError,
                      load_settings, valid_codex_model)

JUDGMENT = {"critic", "devils_advocate", "strategist", "analyst"}
EXECUTION = {"test_author", "implementer"}
EFFORT_ORDER = ["none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"]


def validate_runtime(runtime):
    if not isinstance(runtime, dict) or runtime.get("host") != "codex":
        raise ValueError("runtime must describe the live Codex host")
    for key in ("delegation", "overrides_allowed"):
        if key in runtime and type(runtime[key]) is not bool:
            raise ValueError(f"runtime.{key} must be a boolean")
    for key in ("model_parameter", "effort_parameter", "inherited_model", "inherited_effort"):
        if runtime.get(key) is not None and (not isinstance(runtime[key], str) or not runtime[key]):
            raise ValueError(f"runtime.{key} must be a nonempty string or null")
    models = runtime.get("models", {})
    if not isinstance(models, dict) or any(
            not isinstance(model, str) or not isinstance(efforts, list)
            or any(not isinstance(effort, str) for effort in efforts)
            for model, efforts in models.items()):
        raise ValueError("runtime.models must map advertised model IDs to supported effort lists")
    context = runtime.get("override_context", {})
    if not isinstance(context, dict) or any(
            not isinstance(key, str) or not key or type(value) not in (str, bool)
            for key, value in context.items()):
        raise ValueError("runtime.override_context must contain supported context arguments")
    parameters = [runtime.get("model_parameter"), runtime.get("effort_parameter")]
    if parameters[0] and parameters[0] == parameters[1]:
        raise ValueError("model and effort parameters must be distinct")
    if any(key in context for key in parameters if key):
        raise ValueError("context arguments cannot overwrite model or effort")


def resolve(settings, role, runtime, *, complex_work=False, escalation=False,
            model=None, effort=None, availability_fallback=False):
    validate_runtime(runtime)
    role = role.replace("-", "_")
    if role not in CODEX_ROLES:
        raise ValueError(f"unknown role: {role}")
    if model is not None and not valid_codex_model(model):
        raise ValueError("invalid Codex model override; Claude aliases are not Codex models")
    if effort is not None and effort not in CODEX_EFFORTS:
        raise ValueError("invalid Codex effort override")

    wanted_model = model if model is not None else settings.get(f"codex_model_{role}", settings["codex_model"])
    base_effort = settings["codex_effort_judgment"] if role in JUDGMENT else "medium"
    wanted_effort = effort if effort is not None else settings.get(f"codex_effort_{role}", base_effort)
    # Invocation overrides and inheritance are deliberate choices. Never raise either.
    if role in EXECUTION and (complex_work or escalation) and effort is None:
        higher = settings["codex_effort_complex"]
        if wanted_effort != "inherit" and higher != "inherit":
            wanted_effort = max((wanted_effort, higher), key=EFFORT_ORDER.index)

    args, notes = {}, []
    result = {"role": role.replace("_", "-"),
              "requested": {"model": wanted_model, "effort": wanted_effort},
              "dispatch_args": args, "notes": notes,
              "status": "planned", "confirmed": False,
              "selection": {"model": runtime.get("inherited_model"),
                            "effort": runtime.get("inherited_effort"), "source": "inherited"}}
    if not runtime.get("delegation", False):
        result["status"] = "inline"
        notes.append("No authorized worker dispatch: use the current session; review is a self-check.")
        return result
    if availability_fallback:
        args.update(runtime.get("override_context", {}))
        notes.append("Availability fallback: retry once without model or effort overrides; confirm the host result.")
        return result
    if not runtime.get("overrides_allowed", False):
        notes.append("Host instructions do not permit overrides; inherit the host settings.")
        return result

    model_parameter, effort_parameter = runtime.get("model_parameter"), runtime.get("effort_parameter")
    models = runtime.get("models", {})
    selected_model = runtime.get("inherited_model")
    if wanted_model != "inherit":
        if not model_parameter:
            notes.append("Model selection is unavailable; the worker inherits the host model.")
        elif wanted_model not in models:
            notes.append(f"Model {wanted_model} is not advertised; inherit model and effort instead.")
            return result
        else:
            args[model_parameter] = wanted_model
            selected_model = wanted_model

    if wanted_effort != "inherit":
        if not effort_parameter:
            notes.append("Effort selection is unavailable; the host resolves effort.")
        elif selected_model not in models or wanted_effort not in models[selected_model]:
            args.clear()
            notes.append(f"Cannot verify {wanted_effort} effort for the selected model; inherit both settings.")
            return result
        else:
            args[effort_parameter] = wanted_effort

    if args:
        selected_effort = args.get(effort_parameter)
        if selected_effort is None and model_parameter not in args:
            selected_effort = runtime.get("inherited_effort")
        # A model-only change may select a different host default effort. Do not guess it.
        result["selection"] = {"model": selected_model, "effort": selected_effort,
                               "source": "requested overrides"}
        args.update(runtime.get("override_context", {}))
        notes.append("Pass dispatch_args to the live worker tool; these settings are requested, not confirmed.")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", default=".claude/sdd.local.md")
    parser.add_argument("--runtime", required=True, help="JSON file with observed live capabilities")
    parser.add_argument("--role", required=True)
    parser.add_argument("--complex", action="store_true", dest="complex_work")
    parser.add_argument("--escalation", action="store_true")
    parser.add_argument("--model", help="explicit invocation preference; takes precedence")
    parser.add_argument("--effort", help="explicit invocation preference; takes precedence")
    parser.add_argument("--availability-fallback", action="store_true")
    args = parser.parse_args()
    try:
        settings = load_settings(args.settings)
        runtime = json.loads(Path(args.runtime).read_text())
        result = resolve(settings, args.role, runtime, complex_work=args.complex_work,
                         escalation=args.escalation, model=args.model, effort=args.effort,
                         availability_fallback=args.availability_fallback)
    except (SettingsError, ValueError, OSError, UnicodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1
    print(json.dumps({"ok": True, **result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
