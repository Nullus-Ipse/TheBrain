"""
ui/scroll.py

Autoscroll helper for Streamlit.
Scrolls the main Streamlit app viewport to the newest content.
"""

import streamlit as st


def autoscroll() -> None:
    st.html(
        """
        <script>
        (() => {
            function scrollToBottom() {
                const doc = window.parent?.document || document;

                // Streamlit's main app viewport.
                const main = doc.querySelector(
                    '[data-testid="stAppViewContainer"]'
                );

                if (main) {
                    main.scrollTo({
                        top: main.scrollHeight,
                        behavior: "smooth"
                    });
                    return;
                }

                // Fallbacks for different Streamlit layouts/versions.
                const candidates = [
                    doc.querySelector('[data-testid="stMain"]'),
                    doc.querySelector('section.main'),
                    doc.documentElement,
                    doc.body
                ];

                for (const element of candidates) {
                    if (element && element.scrollHeight > element.clientHeight) {
                        element.scrollTo({
                            top: element.scrollHeight,
                            behavior: "smooth"
                        });
                        break;
                    }
                }
            }

            // Give Streamlit time to finish rendering the result.
            setTimeout(scrollToBottom, 50);
            setTimeout(scrollToBottom, 150);
            setTimeout(scrollToBottom, 300);
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )