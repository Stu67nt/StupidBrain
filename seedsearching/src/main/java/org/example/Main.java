package org.example;

import com.seedfinding.mcbiome.source.BiomeSource;
import com.seedfinding.mcbiome.source.OverworldBiomeSource;
import com.seedfinding.mccore.block.Block;
import com.seedfinding.mccore.block.Blocks;
import com.seedfinding.mccore.rand.ChunkRand;
import com.seedfinding.mccore.rand.seed.WorldSeed;
import com.seedfinding.mccore.state.Dimension;
import com.seedfinding.mccore.util.block.BlockBox;
import com.seedfinding.mccore.util.data.Pair;
import com.seedfinding.mccore.util.math.DistanceMetric;
import com.seedfinding.mccore.util.pos.BPos;
import com.seedfinding.mccore.util.pos.CPos;
import com.seedfinding.mccore.version.MCVersion;
import com.seedfinding.mcfeature.loot.item.Items;
import com.seedfinding.mcfeature.misc.SpawnPoint;
import com.seedfinding.mcfeature.structure.RuinedPortal;
import com.seedfinding.mcfeature.structure.generator.structure.RuinedPortalGenerator;
import com.seedfinding.mcterrain.TerrainGenerator;
import com.seedfinding.mcterrain.terrain.OverworldTerrainGenerator;

import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.function.Supplier;
/*
GOAL:
Find a seed with a ruined portal within 100 blocks of spawn meeting following criteria.
- Should contain at least 27 iron nuggets
- Contains one of fire charge, flint and steel,
- 6 or more obsidian
 */

public class Main {
    static void main() {
        MCVersion version = MCVersion.v1_16_1;
        ChunkRand rand = new ChunkRand();
        RuinedPortal portal = new RuinedPortal(Dimension.OVERWORLD, version);
        RuinedPortalGenerator rpg = new RuinedPortalGenerator(version);

        IO.println("Beginning search");

        for (long worldSeed = 1; worldSeed < 1000000000L; worldSeed++){
            CPos rpPos = portal.getInRegion(worldSeed, 0, 0, rand);
            BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, worldSeed);


            if (rpPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > 6){
                continue;
            }

            TerrainGenerator otg = new TerrainGenerator(obs) {
                @Override
                public Dimension getDimension() {
                    return null;
                }

                @Override
                public int getWorldHeight() {
                    return 0;
                }

                @Override
                public Block getDefaultBlock() {
                    return null;
                }

                @Override
                public Block getDefaultFluid() {
                    return null;
                }

                @Override
                protected void sampleNoiseColumnOld(double[] buffer, int x, int z, double depth, double scale) {

                }

                @Override
                public int getHeightOnGround(int x, int z) {
                    return 0;
                }

                @Override
                public int getFirstHeightInColumn(int x, int z, Predicate<Block> predicate) {
                    return 0;
                }

                @Override
                public Block[] getColumnAt(int x, int z) {
                    return new Block[0];
                }

                @Override
                public Block[] getColumnAt(int x, int z, List<Pair<Supplier<Integer>, BlockBox>> jigsawBoxes, List<BPos> jigsawJunction) {
                    return new Block[0];
                }

                @Override
                public Block[] getBiomeColumnAt(int x, int z) {
                    return new Block[0];
                }

                @Override
                public Block[] getBiomeColumnAt(int x, int z, List<Pair<Supplier<Integer>, BlockBox>> jigsawBoxes, List<BPos> jigsawJunction) {
                    return new Block[0];
                }

                @Override
                public Block[] getBedrockColumnAt(int x, int z) {
                    return new Block[0];
                }

                @Override
                public Block[] getBedrockColumnAt(int x, int z, List<Pair<Supplier<Integer>, BlockBox>> jigsawBoxes, List<BPos> jigsawJunction) {
                    return new Block[0];
                }

                @Override
                public Optional<Block> getBlockAt(int x, int y, int z) {
                    return Optional.empty();
                }
            };
            rpg.generate(otg, rpPos);
            var loot = portal.getLoot(worldSeed, rpg, rand, false);

//            boolean has27nuggets = false;
//            for (var chest: loot) {
//                if (chest.containsAtLeast(Items.IRON_NUGGET, 27)) {
//                    has27nuggets = true;
//                    break;
//                }
//            }

            boolean fireCheck = false;
            for (var chest: loot) {
                if (chest.containsAtLeast(Items.FIRE_CHARGE, 1)) {
                    fireCheck = true;
                    break;
                }
            }

            boolean has10obi = false;
            for (var chest: loot) {
                if (chest.containsAtLeast(Items.OBSIDIAN, 4)) {
                    has10obi = true;
                    break;
                }
            }

            if (!fireCheck) {
                continue;
            }

//            if (!has27nuggets) {
//               continue;
//            }
            if (!has10obi) {
                continue;
            }


            IO.println("Passed loot check. Checking sisters");

            WorldSeed.getSisterSeeds(worldSeed).asStream().boxed().limit(1000).forEach(fullWorldSeed ->
            {
                BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
                TerrainGenerator sotg = TerrainGenerator.of(sobs);
                CPos spawnPoint = SpawnPoint.getSpawn((OverworldTerrainGenerator) sotg).toChunkPos();
                if (!(portal.canSpawn(rpPos, sobs))){
                    return;
                }

                if (spawnPoint.distanceTo(rpPos, DistanceMetric.CHEBYSHEV) > 6) {
                    return;
                }

                System.out.printf("seed: %s (%s %s) \n", fullWorldSeed, rpPos.getX()*16, rpPos.getZ()*16);
            });
        }


    }
}
