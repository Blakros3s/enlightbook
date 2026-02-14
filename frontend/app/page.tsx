export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          Welcome to EnlightBook
        </h1>
        <p className="text-xl text-center text-muted-foreground mb-8">
          School Management System
        </p>
        <div className="flex justify-center gap-4">
          <a
            href="http://localhost:8000/api/docs/"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg bg-primary px-6 py-3 text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            API Documentation
          </a>
        </div>
      </div>
    </main>
  );
}
