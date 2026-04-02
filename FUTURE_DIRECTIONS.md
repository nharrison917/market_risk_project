# Future Directions

## Regime Detection and the Allocation Decision

The current dashboard identifies *retrospective* regime episodes — periods where the 60-day
SPY-TLT correlation exceeded 0.2 for at least 21 consecutive trading days. This is useful for
historical analysis and for explaining the thesis, but it does not answer the actionable question:

**"At what point does an investor know they are in a regime shift, and when should they act?"**

This is the honest follow-up to the current work, and it is meaningfully harder than the analysis
already done.

---

### The Timing Problem

Regime detection is fundamentally a real-time inference problem, not a labeling problem.
The 21-day sustained breakdown threshold was chosen because it filters noise in hindsight.
In real time, an investor observing day 5 of a breakdown cannot know whether it will become
day 21 or reverse at day 8.

Several layers of timing uncertainty compound this:

**1. Window lag**
The 60-day rolling correlation is itself a lagged indicator — it reflects the past 60 trading
days, not the current structural relationship. By the time a regime is "confirmed" by the
window, a meaningful portion of the damage may already have occurred. Shorter windows are
noisier; longer windows are slower to respond. There is no free lunch here.

**2. Confirmation delay**
If the decision rule is "act after N consecutive days above threshold," there is an explicit
tradeoff between false positives (acting on noise) and response lag (acting too late to matter
for CVaR or drawdown protection). The 21-day threshold was chosen analytically; the right
threshold for a decision rule may be different and would require backtesting with realistic
transaction costs and rebalancing constraints.

**3. Downstream metric lag**
Even once a regime is confirmed, the impact on CVaR, drawdown, and real yield does not
manifest instantaneously. CVaR is a distributional measure — it only becomes meaningfully
different from the benign-period estimate after enough return observations have accumulated
under the new regime. Drawdown may already be in progress before the regime label is applied.
Real yield changes drive the structural shift but are themselves a monthly indicator with
publication lag.

**4. Regime exit is harder than regime entry**
The current analysis implicitly assumes the investor holds the 60/30/10 allocation during
breakdown and reverts to 60/40 outside it. But in practice, knowing when a breakdown has
*ended* is at least as difficult as knowing when it *started*. A premature exit from the
commodity hedge re-exposes the portfolio before the risk has actually passed.

---

### Potential Approaches Worth Exploring

- **Hidden Markov Model (HMM) on correlation + vol + yield:** A probabilistic regime model
  that estimates the probability of being in a breakdown state at each point in time, rather
  than a hard threshold rule. Produces a continuous signal that can inform gradual rebalancing
  rather than a binary switch.

- **Kalman filter on rolling correlation:** Reduces the lag vs a fixed rolling window by
  weighting recent observations more heavily. More responsive to genuine shifts; also more
  sensitive to noise. Tuning the signal-to-noise ratio is the core challenge.

- **Rule-based trigger with confirmation window:** A structured decision rule: act when
  correlation exceeds threshold X for N days *and* real yield 12-month change exceeds Y.
  Multi-factor confirmation reduces false positives at the cost of additional lag.
  The current regime classification (vol + correlation + drawdown) is already a precursor
  to this approach.

- **Cost-of-being-wrong analysis:** Rather than optimizing detection accuracy, model the
  asymmetric cost of each error type: acting too early (unnecessary commodity drag in a
  non-breakdown) vs acting too late (full drawdown exposure before the hedge is in place).
  The current CVaR analysis already suggests the cost of the hedge in benign periods is low,
  which argues for a lower confirmation threshold — but this has not been formalized.

---

### Why This Matters for the Portfolio Recommendation

The current finding — that 60/30/10 stabilizes tail risk during sustained breakdown episodes —
is analytically sound but implicitly assumes perfect regime knowledge. A real investor cannot
observe the episode label; they can only observe the correlation signal in real time.

If the detection lag is long enough that most of the CVaR benefit has already been realized
(or the drawdown already in progress) by the time the rule triggers, the practical value of
the strategy is reduced. Quantifying this lag-adjusted benefit is the next honest step before
the recommendation becomes truly actionable.

This is an open research question in the regime-switching literature and does not have a
clean solution. Acknowledging it is a sign of analytical rigor, not a weakness in the
current work.
