'use client';

import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export default function HomePage() {
  const [summary, setSummary] = useState({ total_opportunities: 0, converted_opportunities: 0, conversion_rate: 0 });
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [apiAvailable, setApiAvailable] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/reports/sales`)
      .then((res) => res.json())
      .then((data) => setSummary({
        total_opportunities: data.total_opportunities || 0,
        converted_opportunities: data.converted_opportunities || 0,
        conversion_rate: data.conversion_rate || 0,
      }))
      .catch(() => setApiAvailable(false));

    fetch(`${API_URL}/api/opportunities`)
      .then((res) => res.json())
      .then((data) => setOpportunities(data.items || []))
      .catch(() => setApiAvailable(false));
  }, []);

  return (
    <main className="container">
      <h1>Retail Sales Opportunity Propensity Dashboard</h1>
      <p style={{ color: '#94a3b8' }}>Data-driven sales prioritization for conversion forecasting.</p>
      {!apiAvailable && <p role="status">API unavailable. Configure NEXT_PUBLIC_API_URL with the deployed backend URL.</p>}

      <section className="grid">
        <div className="card">
          <div>Total opportunities</div>
          <div className="metric">{summary.total_opportunities}</div>
        </div>
        <div className="card">
          <div>Converted opportunities</div>
          <div className="metric">{summary.converted_opportunities}</div>
        </div>
        <div className="card">
          <div>Conversion rate</div>
          <div className="metric">{(summary.conversion_rate * 100).toFixed(1)}%</div>
        </div>
      </section>

      <section className="section card">
        <h2>Recent opportunities</h2>
        <table>
          <thead>
            <tr>
              <th>Opportunity</th>
              <th>Customer</th>
              <th>Category</th>
              <th>Stage</th>
              <th>Historical outcome</th>
            </tr>
          </thead>
          <tbody>
            {opportunities.slice(0, 8).map((item) => (
              <tr key={item.opportunity_id || item.customer_id}>
                <td>{item.opportunity_id || 'N/A'}</td>
                <td>{item.customer_id || 'N/A'}</td>
                <td>{item.product_category || 'N/A'}</td>
                <td>{item.opportunity_stage || 'N/A'}</td>
                <td><span className="badge">{item.converted === 1 ? 'Converted' : item.converted === 0 ? 'Not converted' : 'Unknown'}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
