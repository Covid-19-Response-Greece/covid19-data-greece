#!/usr/bin/perl -w

use strict;
my $DATE_RANGE=14;

my ($csvName, $datName, $gpName, $pngName) = @ARGV;

open (IN, "<", $csvName);

my @header=split(/,/, <IN>);
my @dates=@header[3 .. $#header];

my @datesRelevant=@dates[$DATE_RANGE .. $#dates];

my @deltasAll;
my @regions;

open (OUT, ">",$datName);

while(<IN>) {
    my ($nameGr,$nameEn,$inh,@cumm)=split(/,/);
    my @delta;
    if($inh) {
        for(my $i=$DATE_RANGE;$i<=$#cumm;$i++) {
                push @delta, ($cumm[$i] - $cumm[$i-$DATE_RANGE]) / $inh * 100000;
        }
        push @deltasAll, \@delta;
        push @regions, $nameEn;
    }
}

for (my $i=0;$i<=$#datesRelevant;$i++) {
    print OUT $datesRelevant[$i]."\t";
    for(my $j=0;$j<=$#deltasAll;$j++) {
        print OUT ${$deltasAll[$j]}[$i]."\t";
    }
    print OUT "\n";
}
close (OUT);

open (OUT, ">" , $gpName);
print OUT "set title \"Cases per 100.000 inh., date range $DATE_RANGE days\"\n";
print OUT "set key left top\n";
print OUT 'set timefmt "%d/%m/%y"'."\n";
print OUT "set xdata time\n";
print OUT "set xtics 10/01, 604800\n";
print OUT "set ytics 0, 10\n";
#print OUT "set xlabel \"foo\" rotate by 90\n";
print OUT 'set output "'.$pngName."\"\n";
#print OUT "set term png medium size 1200,900\n";
print OUT "set term svg size 1200,900 enhanced background rgb 'white'\n";
print OUT "set grid xtics, ytics\n";
print OUT "set nologscale y\n";
print OUT "set samples 400\n";
print OUT "plot ";

my $smooth=
    "";
    #"smooth csplines";
for(my $j=0;$j<$#regions;$j++) {
    print OUT ($j>0 ? "," : "") ." \"$datName\" using 1:" . ($j+2) . " with linespoints $smooth title \"" . $regions[$j]. '"';        
}
print OUT "\n";

for(my $j=0;$j<$#regions;$j++) {
    print OUT 'set output "'.substr($pngName, 0, -4).$j.substr($pngName, -4)."\"\n";
    print OUT "plot \"$datName\" using 1:" . ($j+2) . " with linespoints $smooth title \"" . $regions[$j]. "\"\n";        
}


close OUT;

system "gnuplot $gpName";
system "thunar $pngName";
