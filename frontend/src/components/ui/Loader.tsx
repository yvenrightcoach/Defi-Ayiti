export default function Loader({ label = "Chargement..." }: { label?: string }) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 text-haiti-blue">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-haiti-blue/20 border-t-haiti-blue" />
      <p className="text-sm font-display">{label}</p>
    </div>
  );
}
