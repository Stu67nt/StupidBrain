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
import com.seedfinding.mcfeature.structure.Shipwreck;
import com.seedfinding.mcfeature.structure.generator.structure.ShipwreckGenerator;
import com.seedfinding.mcterrain.TerrainGenerator;

import java.util.LinkedList;
import java.util.List;
import java.util.Objects;

public class ShipwreckFilter {
    private List<Long> seeds = new java.util.ArrayList<>();

    private final int CHUNK_DIST = 8;
    private final String[] INVALID_BIOMES = {"frozen_ocean", "warm_ocean", "lukewarm_ocean"};
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final Shipwreck sw = new Shipwreck(version);
    private final ShipwreckGenerator swg = new ShipwreckGenerator(version);

    public ShipwreckFilter() {}

    public List<Long> checkSeed(long structureSeed) {

        CPos swPos = sw.getInRegion(structureSeed, 0, 0, rand);
        BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, structureSeed);

        if (swPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return seeds;
        }

        TerrainGenerator otg = TerrainGenerator.of(obs);
        swg.generate(otg, swPos);

        boolean ironCheck = checkChest(structureSeed, 7);
        if (!ironCheck) {
            return seeds;
        }
        IO.println(String.format("Hit at seed %s", structureSeed));
        seeds = WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(1000).parallel()
                .filter(fullWorldSeed -> {
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            String biomeName = sobs.getBiome(swPos.getX()*16, 64, swPos.getZ()*16).getName();

            for (String invalidBiome : INVALID_BIOMES) {
                if (Objects.equals(invalidBiome, biomeName)) {
                    return false;
                }
            }

            if (!(sw.canSpawn(swPos, sobs))){
                return false;
            }
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            if (spawnPoint.distanceTo(swPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return false;
            }

            return true;
        }).toList();
        IO.println("Done seed");
        return seeds;
    }

    private boolean checkChest(long structureSeed, int count){
        var loot = sw.getLoot(structureSeed, swg, rand, false);

        boolean itemCheck = false;
        for (var chest: loot) {
            int nuggyCount = chest.getCount(Items.IRON_NUGGET)/9;
            int ingotCount = chest.getCount(Items.IRON_INGOT);

            if ((nuggyCount+ingotCount) > count) {
                itemCheck = true;
                break;
            }
        }
        return itemCheck;
    }
}
