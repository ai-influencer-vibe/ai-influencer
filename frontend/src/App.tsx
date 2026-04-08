const cards = [
  "Influencer registry",
  "Memory state",
  "Generation queue",
  "Asset library",
];

export default function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">AI Influencer Platform</p>
        <h1>Consistency-first operations for digital personas.</h1>
        <p className="lede">
          Create influencers, manage structured memory, and run generation
          pipelines with auditable history.
        </p>
      </section>

      <section className="grid">
        {cards.map((card) => (
          <article key={card} className="panel">
            <h2>{card}</h2>
            <p>UI modules will be connected to the backend services in the next step.</p>
          </article>
        ))}
      </section>
    </main>
  );
}
