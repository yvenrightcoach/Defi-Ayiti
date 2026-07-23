export default function ErrorMessage({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="mx-auto flex max-w-sm flex-col items-center gap-3 rounded-card bg-haiti-red/10 p-6 text-center">
      <p className="text-haiti-red">{message}</p>
      {onRetry && (
        <button type="button" onClick={onRetry} className="btn-game-secondary text-sm">
          Reessayer
        </button>
      )}
    </div>
  );
}
