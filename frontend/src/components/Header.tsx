export function Header() {
  return (
    <header className="h-14 border-b border-border bg-card flex items-center px-6">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-foreground">Imagine Cup</span>
      </div>
      <div className="ml-auto flex items-center gap-4">
        <span className="text-xs text-muted-foreground">
          Portfolio Risk Intelligence · Last updated 2 min ago
        </span>
      </div>
    </header>
  );
}
