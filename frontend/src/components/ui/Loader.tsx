import Mascot from "@/components/ui/Mascot";

export default function Loader({ label = "Chargement..." }: { label?: string }) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-2 text-haiti-blue">
      <Mascot className="h-16 w-16 animate-wiggle" />
      <p className="font-display text-sm">{label}</p>
    </div>
  );
}
