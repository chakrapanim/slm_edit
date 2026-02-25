"""
Mac Foundation Model loader for grammar correction (macOS Tahoe / Apple Intelligence)
Uses Apple's on-device Foundation Model via apple-foundation-models package.
Requires: macOS 26+, Apple Intelligence enabled, pip install apple-foundation-models

Context window: The framework uses a fixed 4,096-token context window per session (cannot be
increased). This loader uses a new session per correction so the transcript does not accumulate
and trigger "Exceeded model context window size" (error -14). Long inputs are truncated to stay
within the limit.
"""

# Optional: only required on macOS with Apple Intelligence
try:
    from applefoundationmodels import Session, apple_intelligence_available
    _MAC_FM_AVAILABLE = True
except ImportError:
    _MAC_FM_AVAILABLE = False
    Session = None
    apple_intelligence_available = lambda: False


# Apple Foundation Models use a fixed 4,096-token context per session (instructions + prompt + response).
# We reserve ~512 for output and ~200 for instructions/prompt wrapper; truncate input by character count.
# Heuristic: ~4 chars per token -> (4096 - 512 - 200) * 4 ≈ 13500 chars.
MAC_FM_CONTEXT_TOKENS = 4096
MAC_FM_MAX_OUTPUT_TOKENS = 512
MAC_FM_MAX_INPUT_CHARS = 12_000  # truncate longer inputs to avoid context window error -14


CORRECTION_INSTRUCTIONS = (
    "You are a proofreading assistant. Your task is to correct the user's text for "
    "typos, spelling, grammar, punctuation, and clarity. "
    "Output only the corrected text, with no explanations, quotes, or extra text."
)

REPHRASING_INSTRUCTIONS = (
    "You are a writing clarity assistant. Your task is to rephrase the user's text to improve "
    "clarity, readability, and conciseness while keeping the same meaning. "
    "Prefer shorter, direct phrasing; remove wordiness and redundancy. "
    "Output only the rephrased text, with no explanations, quotes, or extra text."
)


class MacFoundationModel:
    """
    Wrapper for Mac Foundation Model (Apple Intelligence) for grammar/typo/rephrasing correction.
    Uses a new session per correct() call to avoid exceeding the 4,096-token context window.
    """

    def __init__(self):
        if not _MAC_FM_AVAILABLE:
            raise RuntimeError(
                "Mac Foundation Model is not available. "
                "Install with: pip install apple-foundation-models. "
                "Requires macOS 26+ (Tahoe) with Apple Intelligence enabled."
            )
        if not apple_intelligence_available():
            raise RuntimeError(
                "Apple Intelligence is not available on this device. "
                "Ensure macOS 26+ and Apple Intelligence is enabled in System Settings."
            )
        print("Mac Foundation Model (Apple Intelligence) will be used for correction.")

    def correct(self, text, max_length=512, num_beams=4, timeout_seconds=60, category=None):  # pylint: disable=unused-argument
        """
        Correct grammar, typos, or rephrase text using the Mac Foundation Model.
        Uses a fresh session per call so context does not accumulate (avoids error -14).

        Args:
            text: Input text to correct (truncated to MAC_FM_MAX_INPUT_CHARS if longer)
            max_length: Ignored (kept for API compatibility with T5 loader)
            num_beams: Ignored (kept for API compatibility)
            timeout_seconds: Max seconds to wait for response (default 60); on timeout returns original text.
            category: Optional "Rephrasing" to use rephrasing-specific instructions and prompt.

        Returns:
            Corrected or rephrased text
        """
        if len(text) > MAC_FM_MAX_INPUT_CHARS:
            text = text[:MAC_FM_MAX_INPUT_CHARS].rstrip()
        is_rephrasing = category == "Rephrasing"
        instructions = REPHRASING_INSTRUCTIONS if is_rephrasing else CORRECTION_INSTRUCTIONS
        if is_rephrasing:
            prompt = f"Rephrase the following for clarity and readability. Output only the rephrased text:\n\n{text}"
        else:
            prompt = f"Correct the following text:\n\n{text}"
        # New session per call so transcript never exceeds 4,096-token context window.
        session = Session(instructions=instructions)
        try:
            import threading
            result = [None]
            exc = [None]

            def run():
                try:
                    response = session.generate(prompt, max_tokens=MAC_FM_MAX_OUTPUT_TOKENS)
                    result[0] = (response.text or "").strip()
                except Exception as e:
                    exc[0] = e
                finally:
                    try:
                        session.close()
                    except Exception:
                        pass

            thread = threading.Thread(target=run, daemon=True)
            thread.start()
            thread.join(timeout=timeout_seconds)
            if thread.is_alive():
                try:
                    session.close()
                except Exception:
                    pass
                print(f"Mac Foundation Model timeout after {timeout_seconds}s, using original text")
                return text
            if exc[0]:
                print(f"Mac Foundation Model error: {exc[0]}")
                return text
            out = result[0] or ""
            # Remove common wrappers if the model added them
            for wrapper in ('"', "'", "Corrected text:", "Here is the corrected text:"):
                if out.lower().startswith(wrapper.lower()):
                    out = out[len(wrapper):].strip()
                if out.lower().endswith(wrapper.lower()):
                    out = out[:-len(wrapper)].strip()
            return out if out else text
        except Exception as e:
            print(f"Mac Foundation Model error: {e}")
            return text
        finally:
            try:
                session.close()
            except Exception:
                pass

    def close(self):
        """No-op: sessions are created per correct() call and closed after use."""
        pass


def mac_foundation_model_available():
    """Return True if Mac Foundation Model can be used."""
    return _MAC_FM_AVAILABLE and apple_intelligence_available()
