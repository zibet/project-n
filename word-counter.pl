use strict;

my %words;

my @lines = <>;

warn "counting words\n";

for ( @lines ){
    if ( /^(\S+)/ ){
	$words{ $1 }++;
    }
}

#for ( sort keys %words ){
#    print "$_: $words{$_}\n";
#}

warn "replace words\n";

for ( @lines ){
    if ( /^(\S+)/ ){
	my $word = $1;
	my $regex = quotemeta( $word );
	if ( $words{ $word } < 5){
	    s/$regex/_RARE_/;
	}
    }
    print;
}
