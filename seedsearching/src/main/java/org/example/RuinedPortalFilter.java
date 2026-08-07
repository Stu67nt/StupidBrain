package org.example;

import com.seedfinding.mcbiome.source.BiomeSource;
import com.seedfinding.mcbiome.source.OverworldBiomeSource;
import com.seedfinding.mccore.rand.ChunkRand;
import com.seedfinding.mccore.rand.seed.WorldSeed;
import com.seedfinding.mccore.state.Dimension;
import com.seedfinding.mccore.util.math.DistanceMetric;
import com.seedfinding.mccore.util.pos.CPos;
import com.seedfinding.mccore.version.MCVersion;
import com.seedfinding.mcfeature.loot.item.Item;
import com.seedfinding.mcfeature.loot.item.Items;
import com.seedfinding.mcfeature.misc.SpawnPoint;
import com.seedfinding.mcfeature.structure.RuinedPortal;
import com.seedfinding.mcfeature.structure.generator.structure.RuinedPortalGenerator;
import com.seedfinding.mcterrain.TerrainGenerator;
import com.seedfinding.mcterrain.terrain.OverworldTerrainGenerator;

public class RuinedPortalFilter {
    private long seedMin;
    private long seedMax;

    private final int CHUNK_DIST = 4;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final RuinedPortal portal = new RuinedPortal(Dimension.OVERWORLD, version);
    private final RuinedPortalGenerator rpg = new RuinedPortalGenerator(version);

    public RuinedPortalFilter(long seedMin, long seedMax) {
        this.seedMin = seedMin;
        this.seedMax = seedMax;
    }

    public void run() {
        long structureSeed;
        for (structureSeed = this.seedMin; structureSeed < this.seedMax; structureSeed++){
            checkSeed(structureSeed);
        }
    }


    private void checkSeed(long structureSeed) {
        CPos rpPos = portal.getInRegion(structureSeed, 0, 0, rand);
        BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, structureSeed);

        if (rpPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return;
        }

        TerrainGenerator otg = TerrainGenerator.of(obs);
        rpg.generate(otg, rpPos);
        boolean hasFire = checkChest(structureSeed, Items.FIRE_CHARGE, 1);
        boolean hasNugs = checkChest(structureSeed, Items.IRON_NUGGET, 14);
        boolean hasObi = checkChest(structureSeed, Items.OBSIDIAN, 4);

        if (!hasFire){
            return;
        }

        if (!hasNugs){
            return;
        }

        if (!hasObi){
            return;
        }

        WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(1000).forEach(fullWorldSeed ->
        {
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            if (!(portal.canSpawn(rpPos, sobs))){
                return;
            }

            if (spawnPoint.distanceTo(rpPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return;
            }

            System.out.printf("seed: %s /tp %s ~ %s \n", fullWorldSeed, rpPos.getX()*16, rpPos.getZ()*16);
        });

    }

    private boolean checkChest(long structureSeed, Item item, int count){
        var loot = portal.getLoot(structureSeed, rpg, rand, false);

        boolean itemCheck = false;
        for (var chest: loot) {
            if (chest.containsAtLeast(item, count)) {
                itemCheck = true;
                break;
            }
        }
        return itemCheck;
    }
}
