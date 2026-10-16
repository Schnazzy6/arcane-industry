import java.nio.file.*;
import org.apache.maven.artifact.versioning.*;
public class CheckModRanges {
 public static void main(String[] args) throws Exception {
  int checked=0,failed=0;
  for(String line:Files.readAllLines(Path.of(args[0]))) {
   String[] p=line.split("\t");
   try {
    var range=VersionRange.createFromVersionSpec(p[2]);
    if(!range.containsVersion(new DefaultArtifactVersion(p[3]))) {
     System.out.println("MISMATCH "+line);failed++;
    }
   } catch(Exception e) {System.out.println("INVALID "+line+" "+e);failed++;}
   checked++;
  }
  System.out.println("Static dependency ranges: "+checked+", problems: "+failed);
  if(failed>0)System.exit(1);
 }
}
