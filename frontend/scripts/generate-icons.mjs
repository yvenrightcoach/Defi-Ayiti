// Regenere les icones PWA (public/icons/*.png) a partir des SVG sources.
// `sharp` n'est pas une dependance du projet (inutile a l'execution) :
// installe-le ponctuellement avant de lancer ce script :
//   npm install --no-save sharp && node scripts/generate-icons.mjs
import sharp from "sharp";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const publicDir = new URL("../public/", import.meta.url);

async function render(svgFile, outFile, size) {
  const svg = readFileSync(fileURLToPath(new URL(svgFile, publicDir)));
  await sharp(svg, { density: 384 })
    .resize(size, size)
    .png()
    .toFile(fileURLToPath(new URL(outFile, publicDir)));
  console.log(`wrote ${outFile} (${size}x${size})`);
}

await render("favicon.svg", "icons/icon-192.png", 192);
await render("favicon.svg", "icons/icon-512.png", 512);
await render("favicon.svg", "icons/apple-touch-icon.png", 180);
await render("mascot-icon-maskable.svg", "icons/icon-maskable-512.png", 512);
