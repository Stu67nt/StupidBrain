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
import com.seedfinding.mcfeature.structure.BuriedTreasure;
import com.seedfinding.mcfeature.structure.generator.structure.BuriedTreasureGenerator;
import com.seedfinding.mcterrain.TerrainGenerator;

import java.util.List;

public class BuriedTreasureFilter {
    private List<Long> seeds = new java.util.ArrayList<>();
    private final int CHUNK_DIST = 6;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final BuriedTreasure bt = new BuriedTreasure(version);
    private final BuriedTreasureGenerator btg = new BuriedTreasureGenerator(version);

    public BuriedTreasureFilter() {}

    public List<Long> checkSeed(long structureSeed) {
        CPos btPos = bt.getInRegion(structureSeed, 0, 0, rand);
        BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, structureSeed);

        if (btPos == null) {
            return seeds;
        }

        if (btPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return seeds;
        }

        TerrainGenerator otg = TerrainGenerator.of(obs);
        btg.generate(otg, btPos);

        boolean hasIron = checkChest(structureSeed, Items.IRON_INGOT, 7);
        boolean hasSufficient = checkChest(structureSeed, Items.IRON_INGOT, 4) && checkChest(structureSeed, Items.DIAMOND, 3);

        if (!(hasIron || hasSufficient)){
            return seeds;
        }

        seeds = WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(1000).parallel().filter(fullWorldSeed ->
        {
            BuriedTreasure bt = new BuriedTreasure(version);
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            if (!(bt.canSpawn(btPos, sobs))){
                return false;
            }
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            if (spawnPoint.distanceTo(btPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return false;
            }
            return true;
        }).toList();
        return seeds;
    }

    private boolean checkChest(long structureSeed, Item item, int count){
        var loot = bt.getLoot(structureSeed, btg, rand, false);

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

