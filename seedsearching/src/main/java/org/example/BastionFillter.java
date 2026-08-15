package org.example;

import Xinyuiii.properties.BastionGenerator;
import com.seedfinding.mcbiome.source.BiomeSource;
import com.seedfinding.mccore.rand.ChunkRand;
import com.seedfinding.mccore.state.Dimension;
import com.seedfinding.mccore.util.math.DistanceMetric;
import com.seedfinding.mccore.util.pos.CPos;
import com.seedfinding.mccore.version.MCVersion;
import com.seedfinding.mcfeature.structure.BastionRemnant;

import java.util.List;


public class BastionFillter {
    private List<Long> inputSeeds;
    private List<Long> outputSeeds;
    private final int CHUNK_DIST = 8;
    private final MCVersion version = MCVersion.v1_16_1;


    public BastionFillter(List<Long> inputSeeds) {
        this.inputSeeds = inputSeeds;
    }

    public List<Long> checkSeeds() {
        outputSeeds = inputSeeds.parallelStream().filter(this::checkIndivSeed).toList();
        return outputSeeds;
    }

    private boolean checkIndivSeed(long seed){
        final ChunkRand rand = new ChunkRand();
        final BastionRemnant br = new BastionRemnant(version);
        final BastionGenerator brg = new BastionGenerator(version);

        CPos brPos = br.getInRegion(seed, 0 ,0, rand);
        if (brPos == null){
            return false;
        }

        if (brPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return false;
        }

        if (!(brg.generate(seed, brPos))){
            return false;
        }

        BiomeSource snbs = BiomeSource.of(Dimension.NETHER, version, seed);
        if (!(br.canSpawn(brPos, snbs))){
            return false;
        }

        return true;
    }

    public String getBastionType(BastionGenerator bastionGenerator){
        return bastionGenerator.getType().toString();
    }

}
