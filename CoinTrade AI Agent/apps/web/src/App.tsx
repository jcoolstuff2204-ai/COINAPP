import {
  Activity,
  AlertTriangle,
  BarChart3,
  BookOpen,
  Brain,
  DatabaseZap,
  LineChart,
  ShieldCheck
} from "lucide-react";
import "./styles.css";

const signal = {
  symbol: "BTC-USD",
  status: "Strong candidate",
  opportunity: 76.9,
  risk: 34.4,
  manipulation: 18,
  state: "Momentum ignition",
  entry: "$42,760 - $42,889",
  invalidation: "$42,554",
  thesis:
    "Participation is increasing with positive trade imbalance, stronger volume, and supportive book structure.",
  counter:
    "The setup can fail if order-flow weakens, price chases above the entry zone, or spread expands."
};

function Badge({ children, tone = "neutral" }: { children: string; tone?: "neutral" | "warning" | "good" | "ai" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <section className="metric">
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{detail}</span>
    </section>
  );
}

export default function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <ShieldCheck size={24} />
          <div>
            <strong>QuanTrade</strong>
            <span>Smarter signals. Calmer trading.</span>
          </div>
        </div>
        <nav>
          <a className="active"><Activity size={18} /> Command Center</a>
          <a><BarChart3 size={18} /> Market Scanner</a>
          <a><LineChart size={18} /> Signal Detail</a>
          <a><DatabaseZap size={18} /> Data Health</a>
          <a><Brain size={18} /> Strategy Lab</a>
          <a><BookOpen size={18} /> Journal</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h1>Command Center</h1>
            <p>Paper-trading decision support with deterministic fixture replay.</p>
          </div>
          <div className="status-row">
            <Badge tone="warning">DEMO DATA</Badge>
            <Badge tone="good">Paper mode</Badge>
            <Badge>Live trading unavailable</Badge>
          </div>
        </header>

        <section className="metrics-grid">
          <Metric label="Portfolio equity" value="$10,000.00" detail="Fixture starting balance" />
          <Metric label="Open risk" value="$0.00" detail="No active paper positions" />
          <Metric label="Market regime" value="Risk-on" detail="Fixture classifier" />
          <Metric label="Feed status" value="Healthy" detail="Replay age 2s" />
        </section>

        <section className="content-grid">
          <article className="panel signal-panel">
            <div className="panel-heading">
              <div>
                <h2>{signal.symbol}</h2>
                <p>{signal.state}</p>
              </div>
              <Badge tone="ai">{signal.status}</Badge>
            </div>
            <div className="score-row">
              <Metric label="Opportunity" value={`${signal.opportunity}`} detail="Inspect components" />
              <Metric label="Risk" value={`${signal.risk}`} detail="Separate from opportunity" />
              <Metric label="Manipulation" value={`${signal.manipulation}`} detail="Below block threshold" />
            </div>
            <div className="evidence">
              <h3>AI explanation</h3>
              <p>{signal.thesis}</p>
              <h3>Counter-thesis</h3>
              <p>{signal.counter}</p>
            </div>
            <div className="trade-plan">
              <span>Entry zone <strong>{signal.entry}</strong></span>
              <span>Invalidation <strong>{signal.invalidation}</strong></span>
            </div>
            <button className="primary-action">Create paper order</button>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>Risk Limit Status</h2>
                <p>Risk controls always outrank signal score.</p>
              </div>
              <AlertTriangle size={22} />
            </div>
            <ul className="check-list">
              <li><span /> Data quality valid</li>
              <li><span /> Spread within limit</li>
              <li><span /> Slippage within limit</li>
              <li><span /> Manipulation risk acceptable</li>
              <li><span /> Daily loss limit available</li>
            </ul>
          </article>
        </section>

        <section className="section-band">
          <div className="panel-heading">
            <div>
              <h2>Market Scanner</h2>
              <p>Sorted fixture signal table with opportunity, risk, and execution status separated.</p>
            </div>
            <Badge tone="warning">Replay running</Badge>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Symbol</th>
                  <th>State</th>
                  <th>Opportunity</th>
                  <th>Risk</th>
                  <th>Manipulation</th>
                  <th>Spread</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td>BTC-USD</td>
                  <td>Momentum ignition</td>
                  <td>80.58</td>
                  <td>34.40</td>
                  <td>18.00</td>
                  <td>4.20 bps</td>
                  <td><Badge tone="ai">Strong candidate</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className="content-grid">
          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>Component Contributions</h2>
                <p>Every score is inspectable and strategy-versioned.</p>
              </div>
              <Badge>v0.1.0</Badge>
            </div>
            <div className="waterfall">
              {[
                ["Order flow", "20%", "18.82"],
                ["Volume anomaly", "15%", "12.94"],
                ["Book structure", "15%", "13.20"],
                ["Momentum", "15%", "11.50"],
                ["Market context", "10%", "7.20"],
                ["Volatility setup", "10%", "6.92"]
              ].map(([label, weight, contribution]) => (
                <div className="bar-row" key={label}>
                  <span>{label}</span>
                  <div><i style={{ width: `${Number(contribution) * 4}%` }} /></div>
                  <b>{contribution}</b>
                  <em>{weight}</em>
                </div>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <h2>Data Health</h2>
                <p>Signals suspend when market data quality fails.</p>
              </div>
              <DatabaseZap size={22} />
            </div>
            <dl className="health-grid">
              <dt>Exchange</dt><dd>fixture</dd>
              <dt>Order book</dt><dd>Valid</dd>
              <dt>Checksum</dt><dd>Passed</dd>
              <dt>Last event</dt><dd>2026-01-15 14:05:00 UTC</dd>
              <dt>Invalid messages</dt><dd>0</dd>
              <dt>Replay events</dt><dd>5</dd>
            </dl>
          </article>
        </section>
      </section>
    </main>
  );
}
