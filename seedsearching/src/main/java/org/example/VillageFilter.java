package org.example;

import com.seedfinding.mcbiome.source.BiomeSource;
import com.seedfinding.mcbiome.source.OverworldBiomeSource;
import com.seedfinding.mccore.rand.ChunkRand;
import com.seedfinding.mccore.rand.seed.WorldSeed;
import com.seedfinding.mccore.state.Dimension;
import com.seedfinding.mccore.util.data.Pair;
import com.seedfinding.mccore.util.math.DistanceMetric;
import com.seedfinding.mccore.util.pos.BPos;
import com.seedfinding.mccore.util.pos.CPos;
import com.seedfinding.mccore.version.MCVersion;
import com.seedfinding.mcfeature.loot.item.Item;
import com.seedfinding.mcfeature.loot.item.ItemStack;
import com.seedfinding.mcfeature.loot.item.Items;
import com.seedfinding.mcfeature.misc.SpawnPoint;
import com.seedfinding.mcfeature.structure.Village;
import com.seedfinding.mcterrain.TerrainGenerator;
import com.seedfinding.mcterrain.terrain.OverworldTerrainGenerator;
import profotoce59.properties.VillageGenerator;

import java.util.List;

public class VillageFilter {
    private List<Long> seeds = new java.util.ArrayList<>();
    private final int CHUNK_DIST = 6;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final Village vil = new Village(version);



    public VillageFilter() {}

    public List<Long> checkSeed(long structureSeed) {
        CPos vilPos = vil.getInRegion(structureSeed, 0, 0, rand);

        if (vilPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return seeds;
        }

        seeds = WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(1000).parallel().filter(fullWorldSeed ->
        {
            ChunkRand rand = new ChunkRand();
            Village vil = new Village(version);
            VillageGenerator vilg = new VillageGenerator(version);
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            TerrainGenerator otg = TerrainGenerator.of(sobs);
            if (!vilg.generate(otg, vilPos)) {
                return false;
            }

            if ((vilg.getNumberOfBlackSmith() < 1)){
                return false;
            }
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            TerrainGenerator sotg = TerrainGenerator.of(sobs);
            if (!(vil.canSpawn(vilPos, sobs))){
                return false;
            }

            if (spawnPoint.distanceTo(vilPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return false;
            }
            List<Pair<BPos, List<ItemStack>>> loot = vilg.generateLoot((OverworldTerrainGenerator) sotg, rand);

            boolean hasIron = checkChest(Items.IRON_INGOT, 4, loot);
            boolean hasSufficient = checkChest(Items.IRON_INGOT, 1, loot) && checkChest(Items.DIAMOND, 3, loot);

            if (!(hasIron || hasSufficient)){
                return false;
            }


            return true;
        }).toList();
        return seeds;
    }

    private boolean checkChest(Item item, int count, List<Pair<BPos, List<ItemStack>>> loot) {
        // This function was vibed becuase the library I am using has no docs
        // But the main ai part was the way to get the loot.

        for (var entry : loot) {
            int total = 0;
            for (ItemStack stack : entry.getSecond()) {
                if (stack.getItem().equals(item)) {
                    total += stack.getCount();
                }
            }
            if (total >= count) {
                return true;
            }
        }
        return false;
    }



}

