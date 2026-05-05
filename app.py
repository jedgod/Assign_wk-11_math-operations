import io
import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
try:
    from audio_recorder_streamlit import audio_recorder
    import speech_recognition as sr
    _VOICE_AVAILABLE = True
except ImportError:
    _VOICE_AVAILABLE = False

st.set_page_config(page_title="Advanced Math Explorer", page_icon="🧮", layout="wide")

x, y, z = sp.symbols("x y z")

st.title("🧮 Advanced Interactive Mathematics Explorer")
st.caption("Solve, simplify, graph, differentiate, integrate, and analyze complex equations.")

menu = st.sidebar.radio(
    "Choose Operation",
    [
        "Step-by-Step Solver",
        "Expression Simplifier",
        "Equation Solver",
        "Derivative Calculator",
        "Integral Calculator",
        "Graph Function",
        "Matrix Calculator",
        "Complex Numbers",
        "System of Equations",
    ],
)

# ── Voice / Speech Recorder ─────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("🎤 Voice Input")
if _VOICE_AVAILABLE:
    st.sidebar.caption(
        "Press the mic button, speak your math question, then press it again to stop."
    )
    audio_bytes = audio_recorder(
        pause_threshold=3.0,
        sample_rate=16_000,
        icon_size="2x",
        recording_color="#e8334a",
        neutral_color="#6aa36f",
        key="voice_recorder",
    )
    if audio_bytes:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(io.BytesIO(audio_bytes)) as src:
                audio_data = recognizer.record(src)
            transcript = recognizer.recognize_google(audio_data)
            st.sidebar.success(f"**Heard:** {transcript}")
            st.session_state["voice_transcript"] = transcript
        except sr.UnknownValueError:
            st.sidebar.warning("Could not understand the audio. Please try again.")
        except sr.RequestError as exc:
            st.sidebar.error(f"Speech recognition service error: {exc}")

    if st.session_state.get("voice_transcript"):
        st.sidebar.info(
            f"📋 Last transcript:\n\n**{st.session_state['voice_transcript']}**"
        )
        if st.sidebar.button("Clear transcript"):
            st.session_state["voice_transcript"] = ""
else:
    st.sidebar.warning(
        "Voice recorder not available. Run:\n"
        "`pip install audio-recorder-streamlit SpeechRecognition`"
    )
# ────────────────────────────────────────────────────────────────────────────

import re

def preprocess_math(expr_str):
    """Convert natural math notation to SymPy-parseable Python syntax."""
    s = expr_str.strip()
    # implicit multiplication: digit immediately followed by letter, e.g. 3x -> 3*x, 2xy -> 2*x*y
    s = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', s)
    # implicit multiplication: closing paren/letter followed by letter/open paren, e.g. 2(x+1) -> 2*(x+1)
    s = re.sub(r'([a-zA-Z0-9])(\()', r'\1*\2', s)
    s = re.sub(r'(\))([a-zA-Z0-9])', r'\1*\2', s)
    # caret exponentiation: x^2 -> x**2
    s = s.replace('^', '**')
    return s


def safe_sympify(expr):
    try:
        return sp.sympify(preprocess_math(expr))
    except Exception as e:
        st.error(f"Invalid expression: {e}")
        return None


def _explain_equation(eq_str):
    """Return a list of (label, latex_or_text) step tuples for an equation."""
    steps = []
    # Handle y=expr form: strip leading 'y=' or 'f(x)=' and treat as expr=0
    eq_clean = eq_str.strip()
    leading = re.match(r'^[a-zA-Z](?:\([^)]*\))?\s*=\s*', eq_clean)
    if leading and not re.search(r'[a-zA-Z](?:\([^)]*\))?\s*=\s*.*=', eq_clean):
        # only one '=' and starts with a variable assignment like y= or f(x)=
        eq_clean = eq_clean[leading.end():].strip() + " = 0"
    left, right = eq_clean.split("=", 1)
    lhs = sp.sympify(preprocess_math(left.strip()))
    rhs = sp.sympify(preprocess_math(right.strip()))
    equation = sp.Eq(lhs, rhs)
    steps.append(("Original equation", sp.latex(equation)))

    moved = sp.expand(lhs - rhs)
    if moved != lhs:
        steps.append(("Move all terms to one side", sp.latex(sp.Eq(moved, 0))))

    factored = sp.factor(moved)
    if factored != moved:
        steps.append(("Factor the expression", sp.latex(sp.Eq(factored, 0))))

    solutions = sp.solve(equation, x)
    steps.append(("Solve for x", ", ".join([sp.latex(s) for s in solutions])))

    for i, sol in enumerate(solutions, 1):
        check = sp.simplify(lhs.subs(x, sol) - rhs.subs(x, sol))
        steps.append((f"Verify solution x = {sp.latex(sol)}",
                      f"LHS - RHS = {sp.latex(check)} {'✓' if check == 0 else '✗'}"))
    return steps


def _explain_derivative(expr_str, order):
    steps = []
    expr = sp.sympify(preprocess_math(expr_str))
    steps.append(("Original function f(x)", sp.latex(expr)))
    current = expr
    for i in range(1, order + 1):
        current = sp.diff(current, x)
        label = f"Derivative order {i}"
        steps.append((label, sp.latex(current)))
        if i < order:
            steps.append((f"  Apply differentiation rules again (order {i+1})", ""))
    steps.append(("Final result", sp.latex(current)))
    return steps


def _explain_integral(expr_str, indef=True, a=None, b=None):
    steps = []
    expr = sp.sympify(preprocess_math(expr_str))
    steps.append(("Integrand f(x)", sp.latex(expr)))

    expanded = sp.expand(expr)
    if expanded != expr:
        steps.append(("Expand the integrand", sp.latex(expanded)))

    result = sp.integrate(expanded, x)
    steps.append(("Apply integration rules term by term", sp.latex(result) + " + C"))

    if not indef:
        definite = sp.integrate(expanded, (x, a, b))
        steps.append((f"Evaluate bounds: substitute x={b} minus x={a}",
                      sp.latex(result.subs(x, b)) + " - " + sp.latex(result.subs(x, a))))
        steps.append(("Final definite value", sp.latex(sp.simplify(definite))))
    return steps


def _explain_simplify(expr_str):
    steps = []
    expr = sp.sympify(preprocess_math(expr_str))
    steps.append(("Original expression", sp.latex(expr)))

    expanded = sp.expand(expr)
    if expanded != expr:
        steps.append(("Expand", sp.latex(expanded)))

    factored = sp.factor(expr)
    if factored != expr:
        steps.append(("Factor", sp.latex(factored)))

    simplified = sp.simplify(expr)
    steps.append(("Simplified result", sp.latex(simplified)))
    return steps


if menu == "Step-by-Step Solver":
    st.header("Step-by-Step Solver")
    st.write(
        "Enter a math question below. The solver will detect the type and "
        "walk you through each step with explanations."
    )

    examples = [
        "Solve: y=3x**3-2x+1",
        "Solve: x^2 - 5x + 6 = 0",
        "Differentiate: 3x^3 + 2x",
        "Integrate: x^2 + sin(x)",
        "Simplify: (x^2 - 1) / (x - 1)",
    ]
    st.caption("Natural notation supported: `3x`, `x^2`, `2(x+1)` — no need for `*` or `**`")

    question = st.text_input(
        "Your question",
        "Solve: x**2 - 5*x + 6 = 0",
        help="Start with Solve:, Differentiate:, Integrate:, or Simplify: followed by your expression.",
    )

    deriv_order = 1
    int_type = "Indefinite"
    int_a, int_b = 0.0, 1.0

    q_lower = question.strip().lower()
    if q_lower.startswith("differentiate:"):
        deriv_order = st.number_input("Derivative order", min_value=1, max_value=10, value=1)
    if q_lower.startswith("integrate:"):
        int_type = st.radio("Integral type", ["Indefinite", "Definite"], horizontal=True)
        if int_type == "Definite":
            col1, col2 = st.columns(2)
            int_a = col1.number_input("Lower bound", value=0.0)
            int_b = col2.number_input("Upper bound", value=1.0)

    if st.button("Solve with Steps"):
        try:
            q = question.strip()
            q_low = q.lower()

            if q_low.startswith("solve:"):
                eq_str = q[6:].strip()
                if "=" not in eq_str:
                    st.error("Please include '=' in your equation, e.g.  x**2 - 4 = 0")
                else:
                    steps = _explain_equation(eq_str)
                    for i, (label, content) in enumerate(steps, 1):
                        with st.expander(f"Step {i}: {label}", expanded=True):
                            if content:
                                st.latex(content)
                    st.info(
                        "**What this means:** The solutions are the x-values where the equation holds true — "
                        "the x-intercepts of the curve. They can represent roots, equilibrium points, or "
                        "break-even values depending on the context."
                    )

            elif q_low.startswith("differentiate:"):
                expr_str = q[14:].strip()
                steps = _explain_derivative(expr_str, int(deriv_order))
                for i, (label, content) in enumerate(steps, 1):
                    with st.expander(f"Step {i}: {label}", expanded=True):
                        if content:
                            st.latex(content)
                st.info(
                    "**What this means:** The derivative gives the instantaneous rate of change of f(x). "
                    "It equals the slope of the tangent line at any point x. "
                    "Where it is zero you have a potential maximum or minimum."
                )

            elif q_low.startswith("integrate:"):
                expr_str = q[10:].strip()
                indef = int_type == "Indefinite"
                steps = _explain_integral(expr_str, indef, int_a, int_b)
                for i, (label, content) in enumerate(steps, 1):
                    with st.expander(f"Step {i}: {label}", expanded=True):
                        if content:
                            st.latex(content)
                if indef:
                    st.info(
                        "**What this means:** The antiderivative F(x) + C is the family of functions "
                        "whose derivative equals f(x). The constant C is determined by an initial condition."
                    )
                else:
                    st.info(
                        "**What this means:** The definite integral equals the signed area under "
                        f"the curve between x = {int_a} and x = {int_b}. "
                        "Positive area lies above the x-axis; negative area lies below."
                    )

            elif q_low.startswith("simplify:"):
                expr_str = q[9:].strip()
                steps = _explain_simplify(expr_str)
                for i, (label, content) in enumerate(steps, 1):
                    with st.expander(f"Step {i}: {label}", expanded=True):
                        if content:
                            st.latex(content)
                st.info(
                    "**What this means:** The simplified form is mathematically equivalent to the original "
                    "but uses fewer operations, making it easier to evaluate, differentiate, or integrate."
                )

            else:
                st.warning(
                    "Please start your question with one of:\n"
                    "**Solve:** | **Differentiate:** | **Integrate:** | **Simplify:**"
                )
        except Exception as e:
            st.error(f"Could not solve: {e}")


elif menu == "Expression Simplifier":
    st.header("Simplify Algebraic Expression")
    st.caption("Reduces an expression to its simplest equivalent form.")
    expr_input = st.text_input("Enter expression", "x**2 + 2*x + 1")

    if st.button("Simplify"):
        expr = safe_sympify(expr_input)
        if expr:
            with st.expander("Step 1: Original expression", expanded=True):
                st.latex(sp.latex(expr))
                st.write("This is the expression exactly as entered.")

            expanded_e = sp.expand(expr)
            if expanded_e != expr:
                with st.expander("Step 2: Expand — multiply out brackets and collect like terms", expanded=True):
                    st.latex(sp.latex(expanded_e))
                    st.write("Distribute any products and group similar powers of x together.")

            factored_e = sp.factor(expr)
            if factored_e != expr:
                with st.expander("Step 3: Factor — write as a product of simpler expressions", expanded=True):
                    st.latex(sp.latex(factored_e))
                    st.write("Identify common factors or recognisable patterns (e.g. perfect square, difference of squares).")

            simplified = sp.simplify(expr)
            with st.expander("Final Result: Simplified form", expanded=True):
                st.latex(sp.latex(simplified))

            st.info(
                f"**What this means:** The expression simplifies to "
                f"${sp.latex(simplified)}$. "
                "Both the original and simplified forms are mathematically identical — they produce "
                "the same output for every value of x. "
                "The simplified version has fewer operations, making it faster to evaluate, "
                "easier to differentiate or integrate, and clearer to read."
            )


elif menu == "Equation Solver":
    st.header("Solve Equation")
    st.caption("Finds the value(s) of x that make the equation true.")
    equation_input = st.text_input("Enter equation", "x**2 - 5*x + 6 = 0")

    if st.button("Solve"):
        try:
            left, right = equation_input.split("=", 1)
            lhs_eq = sp.sympify(preprocess_math(left.strip()))
            rhs_eq = sp.sympify(preprocess_math(right.strip()))
            equation = sp.Eq(lhs_eq, rhs_eq)

            with st.expander("Step 1: Original equation", expanded=True):
                st.latex(sp.latex(equation))
                st.write("Read as: the left side must equal the right side.")

            moved = sp.expand(lhs_eq - rhs_eq)
            with st.expander("Step 2: Move all terms to one side (set = 0)", expanded=True):
                st.latex(sp.latex(sp.Eq(moved, 0)))
                st.write("Subtract the right side from both sides so the equation becomes f(x) = 0.")

            factored_eq = sp.factor(moved)
            if factored_eq != moved:
                with st.expander("Step 3: Factor the expression", expanded=True):
                    st.latex(sp.latex(sp.Eq(factored_eq, 0)))
                    st.write("Write as a product of factors. Each factor equated to zero gives a root.")

            solutions = sp.solve(equation, x)
            with st.expander("Step 4: Solve for x", expanded=True):
                st.latex(r"x \in " + sp.latex(solutions))
                st.write(f"Found {len(solutions)} solution(s).")

            for i, sol in enumerate(solutions, 1):
                check = sp.simplify(lhs_eq.subs(x, sol) - rhs_eq.subs(x, sol))
                tick = "\u2713" if check == 0 else "\u2717"
                with st.expander(f"Step 5.{i}: Verify x = {sp.latex(sol)}", expanded=True):
                    st.latex(r"\text{LHS} - \text{RHS} = " + sp.latex(check))
                    st.write(f"Substituting x = {sol} gives LHS \u2212 RHS = {check}  {tick}")

            st.success(f"Solution(s): {solutions}")
            sol_strs = ",\u2002".join([f"$x = {sp.latex(s)}$" for s in solutions])
            st.info(
                f"**What this means:** {sol_strs} "
                "are the exact values of x where the equation holds true. "
                "Geometrically, these are the **x-intercepts** (roots) of the curve "
                f"$f(x) = {sp.latex(moved)}$ \u2014 the points where the graph crosses the x-axis. "
                "In applied problems, roots can represent break-even points, equilibrium states, "
                "or times at which a quantity equals a target value."
            )
        except Exception as e:
            st.error(e)


elif menu == "Derivative Calculator":
    st.header("Derivative Calculator")
    st.caption("Finds the instantaneous rate of change of a function with respect to x.")
    expr_input = st.text_input("Enter function", "sin(x) + x**3")
    order = st.number_input("Derivative order", min_value=1, max_value=10, value=1)

    if st.button("Differentiate"):
        expr = safe_sympify(expr_input)
        if expr:
            with st.expander("Step 1: Original function f(x)", expanded=True):
                st.latex("f(x) = " + sp.latex(expr))
                st.write("This is the function to be differentiated.")

            current = expr
            for i in range(1, int(order) + 1):
                prev = current
                current = sp.diff(current, x)
                ordinal = {1: "1st", 2: "2nd", 3: "3rd"}.get(i, f"{i}th")
                with st.expander(f"Step {i + 1}: Apply differentiation rules ({ordinal} derivative)", expanded=True):
                    st.latex(r"f^{(" + str(i) + r")}(x) = " + sp.latex(current))
                    rules = []
                    for term in sp.Add.make_args(sp.expand(prev)):
                        if term.has(sp.sin) or term.has(sp.cos) or term.has(sp.tan):
                            rules.append("trig rule  (d/dx sin x = cos x, etc.)")
                        if any(a.is_Pow for a in sp.Mul.make_args(term)) or term.is_Pow:
                            rules.append("power rule  (d/dx x\u207f = n\u00b7x\u207f\u207b\u00b9)")
                        if term.has(sp.exp):
                            rules.append("exponential rule  (d/dx e\u02e3 = e\u02e3)")
                        if term.has(sp.log):
                            rules.append("log rule  (d/dx ln x = 1/x)")
                    if rules:
                        st.write("Rules applied: " + ";  ".join(dict.fromkeys(rules)))

            with st.expander("Final Result", expanded=True):
                label = "f'(x)" if int(order) == 1 else f"f\u207d{int(order)}\u207e(x)"
                st.latex(label + " = " + sp.latex(current))

            meanings = {
                1: (
                    f"**What this means:** The first derivative $f'(x) = {sp.latex(current)}$ gives "
                    "the **instantaneous rate of change** of f(x) at every point x. "
                    "It equals the slope of the tangent line to the curve at that point. "
                    "Where $f'(x) > 0$ the function is **increasing**; where $f'(x) < 0$ it is **decreasing**; "
                    "where $f'(x) = 0$ there is a **potential maximum or minimum** (critical point)."
                ),
                2: (
                    f"**What this means:** The second derivative $f''(x) = {sp.latex(current)}$ measures "
                    "the **rate of change of the slope** \u2014 i.e. the **concavity** of f(x). "
                    "Where $f''(x) > 0$ the curve is concave up (\u222a-shaped); "
                    "where $f''(x) < 0$ it is concave down (\u2229-shaped). "
                    "Points where $f''(x) = 0$ with a sign change are **inflection points**."
                ),
            }
            st.info(meanings.get(int(order),
                f"**What this means:** The order-{int(order)} derivative $= {sp.latex(current)}$ "
                "describes how the lower-order derivatives are themselves changing. "
                "Higher-order derivatives are used in Taylor/Maclaurin series expansions "
                "and in physics (e.g. jerk = 3rd derivative of position with respect to time)."
            ))


elif menu == "Integral Calculator":
    st.header("Integral Calculator")
    st.caption("Finds the antiderivative or the signed area under a curve.")
    expr_input = st.text_input("Enter function", "x**2 + sin(x)")
    integral_type = st.radio("Integral Type", ["Indefinite", "Definite"])

    a_bound, b_bound = 0.0, 1.0
    if integral_type == "Definite":
        a_bound = st.number_input("Lower bound", value=0.0)
        b_bound = st.number_input("Upper bound", value=1.0)

    if st.button("Integrate"):
        expr = safe_sympify(expr_input)
        if expr:
            with st.expander("Step 1: Integrand f(x)", expanded=True):
                st.latex("f(x) = " + sp.latex(expr))
                st.write("This is the function to be integrated.")

            expanded_i = sp.expand(expr)
            if expanded_i != expr:
                with st.expander("Step 2: Expand the integrand", expanded=True):
                    st.latex(sp.latex(expanded_i))
                    st.write("Expand so each term can be integrated separately using standard rules.")

            antideriv = sp.integrate(expanded_i, x)
            with st.expander("Step 3: Apply integration rules term by term", expanded=True):
                st.latex(sp.latex(antideriv) + r" + C")
                st.write(
                    "Rules used: power rule \u222bx\u207f dx = x\u207f\u207a\u00b9/(n+1), "
                    "trig rules (\u222bsin x dx = \u2212cos x, etc.), "
                    "and exponential rules where applicable."
                )

            if integral_type == "Indefinite":
                st.success("Antiderivative F(x):")
                st.latex(sp.latex(antideriv) + r" + C")
                st.info(
                    f"**What this means:** $F(x) = {sp.latex(antideriv)} + C$ is the **antiderivative** "
                    "of f(x). Differentiating F(x) returns the original f(x). "
                    "The constant $C$ represents the fact that any vertical shift of F still differentiates back to f. "
                    "It is determined by an initial condition \u2014 e.g. if you know F(0) = 5, you can solve for C."
                )
            else:
                with st.expander(f"Step 4: Evaluate at bounds x = {b_bound} and x = {a_bound}", expanded=True):
                    upper_val = antideriv.subs(x, b_bound)
                    lower_val = antideriv.subs(x, a_bound)
                    st.latex(
                        r"F(" + str(b_bound) + r") - F(" + str(a_bound) + r") = "
                        + sp.latex(upper_val) + r" - " + sp.latex(lower_val)
                    )
                    st.write("Substitute the upper bound then subtract the result at the lower bound (Fundamental Theorem of Calculus).")

                definite_result = sp.simplify(sp.integrate(expanded_i, (x, a_bound, b_bound)))
                with st.expander("Final Result", expanded=True):
                    st.latex(sp.latex(definite_result))
                st.success(f"Definite integral = {definite_result}")

                try:
                    numeric = float(definite_result.evalf())
                    numeric_str = f" \u2248 {numeric:.4f}"
                except Exception:
                    numeric_str = ""

                st.info(
                    f"**What this means:** $\\int_{{{a_bound}}}^{{{b_bound}}} f(x)\\,dx = "
                    f"{sp.latex(definite_result)}{numeric_str}$. "
                    f"This is the **signed area** between the curve $f(x)$ and the x-axis "
                    f"over the interval $[{a_bound},\\,{b_bound}]$. "
                    "Regions **above** the x-axis contribute positive area; "
                    "regions **below** the x-axis contribute negative area. "
                    "In physics this could represent displacement, work done, or accumulated quantity over time."
                )


elif menu == "Graph Function":
    st.header("Graph Function")
    st.caption("Plots f(x) and analyses key features of the curve.")
    expr_input = st.text_input("Enter function f(x)", "sin(x) + x**2")

    col1, col2 = st.columns(2)
    with col1:
        xmin = st.number_input("X min", value=-10.0)
    with col2:
        xmax = st.number_input("X max", value=10.0)

    if st.button("Plot Graph"):
        expr = safe_sympify(expr_input)
        if expr:
            f = sp.lambdify(x, expr, "numpy")
            xs = np.linspace(xmin, xmax, 500)

            try:
                ys = f(xs)

                fig, ax = plt.subplots()
                ax.plot(xs, ys, color="royalblue", linewidth=2)
                ax.axhline(0, color="black", linewidth=0.8)
                ax.axvline(0, color="black", linewidth=0.8)
                ax.set_title(f"Graph of f(x) = {expr_input}")
                ax.set_xlabel("x")
                ax.set_ylabel("f(x)")
                ax.grid(True, linestyle="--", alpha=0.5)
                st.pyplot(fig)

                st.subheader("Step-by-Step Feature Analysis")
                ca, cb = st.columns(2)

                with ca:
                    with st.expander("Step 1: y-intercept  f(0)", expanded=True):
                        try:
                            y_int = sp.simplify(expr.subs(x, 0))
                            st.latex(r"f(0) = " + sp.latex(y_int))
                            st.write("The value of the function when x = 0 — where the curve crosses the y-axis.")
                        except Exception:
                            st.write("Could not evaluate at x = 0.")

                    with st.expander("Step 2: Zeros  (x-intercepts)", expanded=True):
                        try:
                            zeros = sp.solve(expr, x)
                            real_zeros = [z for z in zeros if z.is_real]
                            if real_zeros:
                                for z in real_zeros:
                                    st.latex(r"x = " + sp.latex(z))
                                st.write("Values of x where f(x) = 0 — the curve meets the x-axis here.")
                            else:
                                st.write("No real zeros found in the symbolic solution.")
                        except Exception:
                            st.write("Could not solve symbolically for zeros.")

                with cb:
                    with st.expander("Step 3: Critical points  f'(x) = 0", expanded=True):
                        try:
                            deriv_expr = sp.diff(expr, x)
                            crits = sp.solve(deriv_expr, x)
                            real_crits = [c for c in crits if c.is_real]
                            if real_crits:
                                for c in real_crits[:6]:
                                    fval = sp.simplify(expr.subs(x, c))
                                    d2 = sp.diff(deriv_expr, x).subs(x, c)
                                    nature = "local min" if d2 > 0 else ("local max" if d2 < 0 else "saddle/inflection")
                                    st.latex(r"x = " + sp.latex(c) + r",\; f = " + sp.latex(fval))
                                    st.write(f"  \u2192 {nature} (f''(x) = {sp.latex(d2)})")
                                st.write("Slope is zero at these points — candidates for maxima, minima, or inflection.")
                            else:
                                st.write("No real critical points found on this function.")
                        except Exception:
                            st.write("Could not compute critical points.")

                    with st.expander("Step 4: Approximate range on plotted interval", expanded=True):
                        valid_ys = ys[np.isfinite(ys)]
                        if len(valid_ys):
                            st.write(f"Min f(x) \u2248 {valid_ys.min():.4f}")
                            st.write(f"Max f(x) \u2248 {valid_ys.max():.4f}")
                            st.write(f"on the interval [{xmin}, {xmax}].")

                st.info(
                    f"**What this means:** The graph of $f(x) = {expr_input}$ visualises how the "
                    "output changes as x varies. "
                    "The **y-intercept** shows the starting value at x = 0. "
                    "The **zeros** are where the curve crosses the x-axis. "
                    "The **critical points** (f\u2032(x) = 0) are local highs or lows — the second-derivative test "
                    "confirms whether each is a maximum, minimum, or saddle point. "
                    "Together these features give a complete picture of the function\u2019s behaviour."
                )
            except Exception as e:
                st.error(e)


elif menu == "Matrix Calculator":
    st.header("Matrix Calculator")
    st.caption("Perform matrix operations with step-by-step working and interpretation.")

    matrix_input = st.text_area(
        "Enter matrix rows separated by semicolon",
        "1,2;3,4"
    )

    operation = st.selectbox(
        "Operation",
        ["Determinant", "Inverse", "Transpose", "Eigenvalues"]
    )

    if st.button("Calculate Matrix"):
        try:
            rows_m = matrix_input.split(";")
            matrix = [[float(num) for num in row.split(",")] for row in rows_m]
            M = sp.Matrix(matrix)
            n_m = M.shape[0]

            with st.expander("Step 1: Input matrix", expanded=True):
                st.latex("A = " + sp.latex(M))
                st.write(f"A {M.shape[0]}\u00d7{M.shape[1]} matrix.")

            if operation == "Determinant":
                with st.expander("Step 2: Compute determinant", expanded=True):
                    if n_m == 2:
                        a_m, b_m = M[0, 0], M[0, 1]
                        c_m, d_m = M[1, 0], M[1, 1]
                        st.latex(
                            r"\det(A) = ad - bc = ("
                            + sp.latex(a_m) + r")("
                            + sp.latex(d_m) + r") - ("
                            + sp.latex(b_m) + r")("
                            + sp.latex(c_m) + r")"
                        )
                    else:
                        st.write("For larger matrices SymPy uses LU decomposition (cofactor expansion generalised).")
                result_m = M.det()
                with st.expander("Final Result: det(A)", expanded=True):
                    st.latex(r"\det(A) = " + sp.latex(result_m))
                st.info(
                    f"**What this means:** det(A) = {result_m}. "
                    + ("The determinant is **zero** — the matrix is **singular** (non-invertible). "
                       "The system Ax = b has either no solution or infinitely many solutions, "
                       "and the transformation collapses space onto a lower dimension."
                       if result_m == 0 else
                       "The determinant is **non-zero** — the matrix is **invertible**. "
                       f"The value |det(A)| = {abs(result_m)} is the factor by which the matrix "
                       "scales areas (2D) or volumes (3D) under the linear transformation. "
                       "A negative determinant means the orientation is reversed (reflection).")
                )

            elif operation == "Inverse":
                det_m = M.det()
                with st.expander("Step 2: Check invertibility — det(A) \u2260 0", expanded=True):
                    st.latex(r"\det(A) = " + sp.latex(det_m))
                    if det_m == 0:
                        st.error("det(A) = 0 — this matrix is singular and has no inverse.")
                    else:
                        st.write("det(A) \u2260 0, so the inverse exists.")
                if det_m != 0:
                    result_m = M.inv()
                    with st.expander("Step 3: Compute A\u207b\u00b9 = (1/det) \u00b7 adjugate(A)", expanded=True):
                        st.latex(r"A^{-1} = " + sp.latex(result_m))
                    with st.expander("Step 4: Verify  A \u00b7 A\u207b\u00b9 = I", expanded=True):
                        product_m = sp.simplify(M * result_m)
                        st.latex(r"A \cdot A^{-1} = " + sp.latex(product_m))
                        st.write("Identity matrix confirmed \u2713" if product_m == sp.eye(n_m) else "Verification failed \u2717")
                    st.info(
                        "**What this means:** $A^{-1}$ is the inverse of A. "
                        "Multiplying A by $A^{-1}$ gives the identity matrix I (like dividing by itself). "
                        "In a linear system $Ax = b$, the inverse lets you solve directly as $x = A^{-1}b$, "
                        "without needing row reduction. In transformations, $A^{-1}$ undoes whatever A does."
                    )

            elif operation == "Transpose":
                with st.expander("Step 2: Swap rows and columns", expanded=True):
                    st.write("Element at position (i, j) moves to position (j, i). Rows become columns and vice versa.")
                result_m = M.T
                with st.expander("Final Result: A\u1d40", expanded=True):
                    st.latex(r"A^T = " + sp.latex(result_m))
                is_sym = "symmetric (A = A\u1d40) \u2713" if M == result_m else "not symmetric."
                st.info(
                    f"**What this means:** $A^T$ is the transpose of A. This matrix is {is_sym} "
                    "The transpose appears in dot products ($\\mathbf{{a}} \\cdot \\mathbf{{b}} = \\mathbf{{a}}^T\\mathbf{{b}}$), "
                    "projections, and least-squares regression. "
                    "For rotation matrices, the transpose equals the inverse, making it very efficient to invert."
                )

            else:  # Eigenvalues
                lam = sp.Symbol("lambda")
                char_poly = (M - lam * sp.eye(n_m)).det()
                with st.expander("Step 2: Form the characteristic polynomial  det(A \u2212 \u03bbI) = 0", expanded=True):
                    st.latex(r"\det(A - \lambda I) = " + sp.latex(char_poly) + " = 0")
                    st.write("\u03bb (lambda) represents the unknown eigenvalue. Expand and solve for \u03bb.")
                eigenvects_m = M.eigenvects()
                with st.expander("Step 3: Solve for eigenvalues and eigenvectors", expanded=True):
                    for val, mult, vecs in eigenvects_m:
                        st.latex(r"\lambda = " + sp.latex(val) + r"\quad (\text{multiplicity } " + str(mult) + r")")
                        for v in vecs:
                            st.latex(r"\mathbf{v} = " + sp.latex(v))
                        st.write(f"  Verification: Av = \u03bbv where \u03bb = {val}")
                st.info(
                    "**What this means:** An eigenvalue \u03bb and its eigenvector **v** satisfy $A\\mathbf{v} = \\lambda\\mathbf{v}$. "
                    "The matrix only **scales** v by \u03bb without changing its direction. "
                    "Eigenvalues describe the principal axes and magnitudes of the transformation. "
                    "They are used in Principal Component Analysis (data science), "
                    "structural vibration analysis, Google\u2019s PageRank, and quantum mechanics."
                )

        except Exception as e:
            st.error(e)


elif menu == "Complex Numbers":
    st.header("Complex Number Calculator")
    st.caption("Evaluate complex expressions and interpret their geometric meaning.")

    expr_input = st.text_input("Enter complex expression", "(3 + 4*I) * (2 - I)")

    if st.button("Evaluate Complex Expression"):
        expr = safe_sympify(expr_input)
        if expr:
            with st.expander("Step 1: Original expression", expanded=True):
                st.latex(sp.latex(expr))
                st.write("$I$ is the imaginary unit where $I^2 = -1$.")

            expanded_c = sp.expand(expr)
            if expanded_c != expr:
                with st.expander("Step 2: Expand using the distributive law", expanded=True):
                    st.latex(sp.latex(expanded_c))
                    st.write("Multiply out all brackets and replace $I^2$ with $-1$.")

            result_c = sp.simplify(expr)
            real_part = sp.re(result_c)
            imag_part = sp.im(result_c)

            with st.expander("Step 3: Separate real and imaginary parts", expanded=True):
                st.latex(
                    r"\text{Re}(z) = " + sp.latex(real_part)
                    + r"\qquad \text{Im}(z) = " + sp.latex(imag_part)
                )
                st.write("Group all real terms together and all terms containing I together.")

            with st.expander("Final Result: Standard form  a + bi", expanded=True):
                st.latex("z = " + sp.latex(result_c))

            try:
                modulus_c = sp.simplify(sp.Abs(result_c))
                argument_c = sp.atan2(imag_part, real_part)
                with st.expander("Step 4: Polar form  |z| and arg(z)", expanded=True):
                    st.latex(r"|z| = " + sp.latex(modulus_c))
                    st.latex(r"\arg(z) = " + sp.latex(argument_c))
                    st.write("The modulus is the distance from the origin; the argument is the angle from the positive real axis.")
                st.info(
                    f"**What this means:** The result is $z = {sp.latex(result_c)}$. "
                    f"On the **Argand diagram** (complex plane) this point is at "
                    f"$({sp.latex(real_part)},\\;{sp.latex(imag_part)})$. "
                    f"The **modulus** $|z| = {sp.latex(modulus_c)}$ is its distance from the origin — "
                    "think of it as the \u2018size\u2019 of the complex number. "
                    "The **argument** is the angle it makes with the positive x-axis. "
                    "Complex numbers model rotation and oscillation: multiplying two complex numbers "
                    "adds their angles and multiplies their moduli."
                )
            except Exception:
                st.info(
                    f"**What this means:** The result is $z = {sp.latex(result_c)}$ with "
                    f"real part {sp.latex(real_part)} and imaginary part {sp.latex(imag_part)}."
                )


elif menu == "System of Equations":
    st.header("Solve System of Equations")
    st.caption("Finds the values of x and y that satisfy both equations simultaneously.")

    eq1 = st.text_input("Equation 1", "x + y = 5")
    eq2 = st.text_input("Equation 2", "2*x - y = 1")

    if st.button("Solve System"):
        try:
            left1, right1 = eq1.split("=", 1)
            left2, right2 = eq2.split("=", 1)
            e1 = sp.Eq(sp.sympify(preprocess_math(left1.strip())), sp.sympify(preprocess_math(right1.strip())))
            e2 = sp.Eq(sp.sympify(preprocess_math(left2.strip())), sp.sympify(preprocess_math(right2.strip())))

            with st.expander("Step 1: Original system", expanded=True):
                st.latex(
                    r"\begin{cases}" + sp.latex(e1) + r"\\" + sp.latex(e2) + r"\end{cases}"
                )
                st.write("Find x and y satisfying both equations at the same time.")

            lhs1_s = sp.sympify(preprocess_math(left1.strip())) - sp.sympify(preprocess_math(right1.strip()))
            lhs2_s = sp.sympify(preprocess_math(left2.strip())) - sp.sympify(preprocess_math(right2.strip()))
            with st.expander("Step 2: Rearrange to standard form (= 0)", expanded=True):
                st.latex(sp.latex(sp.Eq(lhs1_s, 0)))
                st.latex(sp.latex(sp.Eq(lhs2_s, 0)))
                st.write("Move all terms to the left side so each equation equals zero.")

            with st.expander("Step 3: Solve by substitution / elimination", expanded=True):
                st.write(
                    "Express one variable from equation 1, substitute into equation 2 "
                    "to get a single-variable equation, then back-substitute."
                )

            solution = sp.solve([e1, e2], (x, y))

            with st.expander("Step 4: Solution", expanded=True):
                if isinstance(solution, dict):
                    for var, val in solution.items():
                        st.latex(sp.latex(var) + " = " + sp.latex(val))
                else:
                    st.write(str(solution))

            if isinstance(solution, dict):
                x_sol = solution.get(x)
                y_sol = solution.get(y)
                if x_sol is not None and y_sol is not None:
                    with st.expander("Step 5: Verify solution", expanded=True):
                        for eq_label, eq_obj in [(eq1, e1), (eq2, e2)]:
                            check_s = sp.simplify(
                                eq_obj.lhs.subs([(x, x_sol), (y, y_sol)])
                                - eq_obj.rhs.subs([(x, x_sol), (y, y_sol)])
                            )
                            tick = "\u2713" if check_s == 0 else "\u2717"
                            st.write(
                                f"Equation `{eq_label}`:  "
                                f"substituting x={x_sol}, y={y_sol} \u2192 remainder = {check_s}  {tick}"
                            )

                    st.success(f"Solution: x = {x_sol},  y = {y_sol}")
                    st.latex(r"x = " + sp.latex(x_sol) + r",\quad y = " + sp.latex(y_sol))
                    st.info(
                        f"**What this means:** The solution $x = {sp.latex(x_sol)},\\; y = {sp.latex(y_sol)}$ "
                        "is the **point of intersection** of the two lines on the coordinate plane. "
                        "It is the only pair of values that satisfies both equations simultaneously. "
                        "In real-world problems this could represent the price and quantity where "
                        "supply meets demand, or the time and distance where two objects meet."
                    )
            else:
                st.write(str(solution))
                st.info(
                    "**What this means:** The system may have **no solution** (the two lines are parallel "
                    "and never intersect) or **infinitely many solutions** (the two equations describe "
                    "the same line, so every point on it is a solution)."
                )

        except Exception as e:
            st.error(e)
