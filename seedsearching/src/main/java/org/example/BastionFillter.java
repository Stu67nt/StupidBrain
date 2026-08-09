package org.example;

import Xinyuiii.properties.BastionGenerator;
import com.seedfinding.mcbiome.source.BiomeSource;
import com.seedfinding.mccore.rand.ChunkRand;
import com.seedfinding.mccore.rand.seed.WorldSeed;
import com.seedfinding.mccore.state.Dimension;
import com.seedfinding.mccore.util.math.DistanceMetric;
import com.seedfinding.mccore.util.pos.CPos;
import com.seedfinding.mccore.version.MCVersion;
import com.seedfinding.mcfeature.structure.BastionRemnant;


public class BastionFillter {
    private long seedMin;
    private long seedMax;

    private final int CHUNK_DIST = 5;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final BastionRemnant br = new BastionRemnant(version);
    private final BastionGenerator brg = new BastionGenerator(version);

    public BastionFillter(long seedMin, long seedMax) {
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
        CPos brPos = br.getInRegion(structureSeed, 0 ,0, rand);
        if (brPos == null){
            return;
        }

        if (brPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return;
        }

        if (!(brg.generate(structureSeed, brPos))){
            return;
        }

        WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(10).forEach(fullWorldSeed ->
        {
            BiomeSource snbs = BiomeSource.of(Dimension.NETHER, version, fullWorldSeed);
            if (!(br.canSpawn(brPos, snbs))){
                return;
            }

            if (CPos.ZERO.distanceTo(brPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return;
            }

            System.out.printf("seed: %s /tp %s ~ %s \n", fullWorldSeed, brPos.getX()*16, brPos.getZ()*16);
        });
    }

    public String getBastionType(BastionGenerator bastionGenerator){
        return bastionGenerator.getType().toString();
    }

}
