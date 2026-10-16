import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.file.*;
import javax.imageio.ImageIO;

/** Technical game-asset export; original generated artwork is kept separately. */
public class PrepareItemTexture {
  public static void main(String[] args) throws Exception {
    BufferedImage source=ImageIO.read(Path.of(args[0]).toFile());
    if(source==null || !source.getColorModel().hasAlpha()) throw new IllegalArgumentException("PNG needs alpha");
    int size=32;
    BufferedImage texture=new BufferedImage(size,size,BufferedImage.TYPE_INT_ARGB);
    Graphics2D g=texture.createGraphics();
    g.setComposite(AlphaComposite.Src);
    g.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
    g.drawImage(source,0,0,size,size,null);g.dispose();
    int transparent=0,visible=0;
    for(int y=0;y<size;y++)for(int x=0;x<size;x++) {
      int a=texture.getRGB(x,y)>>>24;
      if(a==0) transparent++;else visible++;
    }
    if(transparent<50 || visible<25) throw new IllegalArgumentException("Invalid item silhouette/alpha");
    Path output=Path.of(args[1]);Files.createDirectories(output.getParent());
    ImageIO.write(texture,"PNG",output.toFile());
    System.out.println(output.getFileName()+": 32x32, visible="+visible+", transparent="+transparent);
  }
}
