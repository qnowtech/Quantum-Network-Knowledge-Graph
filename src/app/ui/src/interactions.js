import NVL from "@neo4j-nvl/base";
import {
  ClickInteraction,
  DragNodeInteraction,
  HoverInteraction,
  PanInteraction,
  ZoomInteraction,
} from "@neo4j-nvl/interaction-handlers";

export default (parentContainer) => {
  const nodes = [{ id: "0" }, { id: "1" }];
  const rels = [{ id: "10", from: "0", to: "1" }];
  const myNvl = new NVL(parentContainer, nodes, rels, {
    // Opciones de ForceDirected
    enableCytoscape: true, // Auto-switch a CoseBilkent para grafos pequeños
    enableVerlet: true, // Usar nuevo motor de física (recomendado)
    intelWorkaround: false, // Solo activar si hay problemas con GPUs Intel
  });
  new ZoomInteraction(myNvl);
  new PanInteraction(myNvl);
  new DragNodeInteraction(myNvl);
  new ClickInteraction(myNvl, { selectOnClick: true });
  new HoverInteraction(myNvl, { drawShadowOnHover: true });

  return myNvl;
};
