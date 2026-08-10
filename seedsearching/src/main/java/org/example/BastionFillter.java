package org.example;

import Xinyuiii.properties.BastionGenerator;
import com.seedfinding.mcbiome.source.BiomeSource;
import com.seedfinding.mccore.rand.ChunkRand;
import com.seedfinding.mccore.state.Dimension;
import com.seedfinding.mccore.util.math.DistanceMetric;
import com.seedfinding.mccore.util.pos.CPos;
import com.seedfinding.mccore.version.MCVersion;
import com.seedfinding.mcfeature.structure.BastionRemnant;

import java.util.LinkedList;


public class BastionFillter {
    private LinkedList<Long> inputSeeds;
    private LinkedList<Long> outputSeeds = new LinkedList<Long>();
    private final int CHUNK_DIST = 24;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final BastionRemnant br = new BastionRemnant(version);
    private final BastionGenerator brg = new BastionGenerator(version);

    public BastionFillter(LinkedList<Long> inputSeeds) {
        this.inputSeeds = inputSeeds;
    }

    public LinkedList<Long> checkSeeds() {
        for (int i = 0; i < inputSeeds.size(); i++){
            long structureSeed = this.inputSeeds.get(i);
            CPos brPos = br.getInRegion(structureSeed, 0 ,0, rand);
            if (brPos == null){
                continue;
            }

            if (brPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
                continue;
            }

            if (!(brg.generate(structureSeed, brPos))){
                continue;
            }

            BiomeSource snbs = BiomeSource.of(Dimension.NETHER, version, structureSeed);
            if (!(br.canSpawn(brPos, snbs))){
                continue;
            }

            if (CPos.ZERO.distanceTo(brPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                continue;
            }

            IO.println(String.format("Found Valid bastion %s", brPos));

            outputSeeds.add(structureSeed);
        }


        return outputSeeds;
    }

    public String getBastionType(BastionGenerator bastionGenerator){
        return bastionGenerator.getType().toString();
    }

}
