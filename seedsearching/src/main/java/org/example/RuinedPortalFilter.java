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

import java.util.LinkedList;

public class RuinedPortalFilter {
    private LinkedList<Long> seeds = new LinkedList<Long>();
    private final int CHUNK_DIST = 6;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final RuinedPortal portal = new RuinedPortal(Dimension.OVERWORLD, version);
    private final RuinedPortalGenerator rpg = new RuinedPortalGenerator(version);

    public RuinedPortalFilter() {}

    public LinkedList<Long> checkSeed(long structureSeed) {
        CPos rpPos = portal.getInRegion(structureSeed, 0, 0, rand);
        BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, structureSeed);

        if (rpPos == null){
            return seeds;
        }

        if (rpPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return seeds;
        }

        TerrainGenerator otg = TerrainGenerator.of(obs);
        if (!rpg.generate(otg, rpPos)) {
            return seeds;
        }
        boolean hasFire = checkChest(structureSeed, Items.FIRE_CHARGE, 1);
        boolean hasNugs = checkChest(structureSeed, Items.IRON_NUGGET, 14);
        boolean hasObi = checkChest(structureSeed, Items.OBSIDIAN, 4);

        if (!hasFire){
            return seeds;
        }

        if (!hasNugs){
            return seeds;
        }

        if (!hasObi){
            return seeds;
        }
        IO.println(String.format("hit at seed %s", structureSeed));
        WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(100).forEach(fullWorldSeed ->
        {
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            if (!(portal.canSpawn(rpPos, sobs))){
                return;
            }

            if (spawnPoint.distanceTo(rpPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return;
            }

            seeds.add(fullWorldSeed);
        });
        return seeds;
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
